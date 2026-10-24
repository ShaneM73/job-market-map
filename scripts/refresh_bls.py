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
    for i in range(2):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
            d = json.loads(raw)
            if d.get('status') == 'REQUEST_SUCCEEDED':
                return d['Results']['series']
            log('BLS said:', d.get('status'), d.get('message'))
        except urllib.error.HTTPError as e:
            log('BLS HTTP error:', e.code, e.read()[:300])
        except Exception as e:
            log('BLS fetch failed:', repr(e))
        time.sleep(3 * (i + 1))
    return []


# Fallback: FRED (St. Louis Fed) republishes the same BLS series as CSV without a key.
ABBR = {'01':'AL','02':'AK','04':'AZ','05':'AR','06':'CA','08':'CO','09':'CT','10':'DE','11':'DC','12':'FL','13':'GA','15':'HI','16':'ID','17':'IL','18':'IN','19':'IA','20':'KS','21':'KY','22':'LA','23':'ME','24':'MD','25':'MA','26':'MI','27':'MN','28':'MS','29':'MO','30':'MT','31':'NE','32':'NV','33':'NH','34':'NJ','35':'NM','36':'NY','37':'NC','38':'ND','39':'OH','40':'OK','41':'OR','42':'PA','44':'RI','45':'SC','46':'SD','47':'TN','48':'TX','49':'UT','50':'VT','51':'VA','53':'WA','54':'WV','55':'WI','56':'WY'}


def fred(series_id, start):
    url = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={start}-01-01'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (job-market-map refresh)'})
    for i in range(2):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                txt = r.read().decode('utf-8', 'replace')
            pts = {}
            for line in txt.splitlines()[1:]:
                parts = line.split(',')
                if len(parts) >= 2 and parts[1] not in ('.', ''):
                    try: pts[parts[0][:7]] = float(parts[1])
                    except ValueError: pass
            return pts
        except Exception as e:
            log('FRED fetch failed:', series_id, repr(e)); time.sleep(2)
    return {}


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
    log(f'BLS API series with data: {got} of {2 * len(ids)}')
    if got < 2 * len(ids):
        log('falling back to FRED for the missing series')
        for f in ids:
            ab = ABBR[f]
            if not series.get(f'LASST{f}0000000000003'): series[f'LASST{f}0000000000003'] = fred(f'{ab}UR', year - 1); time.sleep(0.3)
            if not series.get(f'SMS{f}000000000000001'): series[f'SMS{f}000000000000001'] = fred(f'{ab}NA', year - 1); time.sleep(0.3)
        got = sum(1 for v in series.values() if v)
        log(f'after FRED: {got} of {2 * len(ids)}')
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
        r['source'] = f'BLS LAUS (state unemployment, SA) and CES state nonfarm employment (SA), via api.bls.gov / FRED, {latest}'
    with open(os.path.join(ROOT, 'states.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    log('wrote states.csv for', latest)


if __name__ == '__main__':
    main()
