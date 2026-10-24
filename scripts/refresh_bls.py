#!/usr/bin/env python3
"""Refresh data/states.csv from the BLS public API (v1 needs no key; 25 requests/day, 10 series each).

Series used, per state FIPS ss:
  LASSTss0000000000003  unemployment rate, seasonally adjusted (LAUS)
  SMSss000000000000001  total nonfarm employment, seasonally adjusted, thousands (CES state)

Writes: state, fips, period (YYYY-MM of the latest month with a value), unemployment_rate,
unemployment_rate_year_ago, unemployment_change_pts, jobs_thousands, jobs_change_12mo_thousands,
jobs_change_12mo_pct, source. The nonfarm change is shown for every state (BLS's release only
flags statistically significant ones; see README).
If the API returns nothing usable the file is left unchanged and the script exits 1.
"""
import csv, json, os, sys, time, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
API = 'https://api.bls.gov/publicAPI/v2/timeseries/data/' if os.environ.get('BLS_API_KEY') else 'https://api.bls.gov/publicAPI/v1/timeseries/data/'
KEY = os.environ.get('BLS_API_KEY', '')


def log(*a): print(*a, file=sys.stderr, flush=True)


def fetch(series, start, end):
    body = {'seriesid': series, 'startyear': str(start), 'endyear': str(end)}
    if KEY: body['registrationkey'] = KEY
    req = urllib.request.Request(API, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'User-Agent': 'job-market-map refresh'})
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read())
            if d.get('status') == 'REQUEST_SUCCEEDED':
                return d['Results']['series']
            log('BLS said:', d.get('status'), d.get('message'))
        except Exception as e:
            log('fetch failed:', e)
        time.sleep(3 * (i + 1))
    return []


def main():
    with open(os.path.join(ROOT, 'states.csv'), newline='') as f:
        rows = list(csv.DictReader(f))
    fips = {r['state']: r['fips'] for r in rows}
    ids = sorted(fips.values())
    year = time.gmtime().tm_year
    series = {}
    for prefix, fmt in (('u', 'LASST{}0000000000003'), ('j', 'SMS{}000000000000001')):
        codes = [fmt.format(f) for f in ids]
        for k in range(0, len(codes), 10 if not KEY else 50):
            for s in fetch(codes[k:k + (10 if not KEY else 50)], year - 1, year):
                pts = {}
                for o in s.get('data', []):
                    if o['period'].startswith('M') and o['period'] != 'M13':
                        try: pts[f"{o['year']}-{o['period'][1:]}"] = float(o['value'])
                        except ValueError: pass
                series[s['seriesID']] = pts
            time.sleep(1)
    got = sum(1 for v in series.values() if v)
    log(f'series with data: {got} of {2 * len(ids)}')
    if got < len(ids):
        log('too little data; leaving states.csv unchanged'); sys.exit(1)
    # latest month present in the unemployment series
    latest = max(max(v) for k, v in series.items() if k.startswith('LASST') and v)
    y, m = latest.split('-'); year_ago = f'{int(y) - 1}-{m}'
    for r in rows:
        f = r['fips']; u = series.get(f'LASST{f}0000000000003', {}); j = series.get(f'SMS{f}000000000000001', {})
        if latest in u:
            r['period'] = latest; r['unemployment_rate'] = u[latest]
            r['unemployment_rate_year_ago'] = u.get(year_ago, '')
            r['unemployment_change_pts'] = round(u[latest] - u[year_ago], 1) if year_ago in u else ''
        if latest in j and year_ago in j:
            r['jobs_thousands'] = j[latest]
            r['jobs_change_12mo_thousands'] = round(j[latest] - j[year_ago], 1)
            r['jobs_change_12mo_pct'] = round((j[latest] / j[year_ago] - 1) * 100, 1)
        r['source'] = f'BLS LAUS (state unemployment, SA) and CES state nonfarm employment (SA), via api.bls.gov, {latest}'
    with open(os.path.join(ROOT, 'states.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    log('wrote states.csv for', latest)


if __name__ == '__main__':
    main()
