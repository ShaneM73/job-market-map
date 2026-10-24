# US job market 2026 — 3-D map infographic

A single-page, data-driven 3-D map of the US labor market, built for geospatial-science students and
professionals. States rise and sink with the chosen measure; pins mark the ten metros where geospatial
work concentrates; four short chapters walk through the story.

**Layers:** unemployment rate · change vs. a year ago · 12-month nonfarm job growth · geospatial hubs
**Markers:** hub pins (height = hub score, hover for the case for each), metro dots (job winners/losers)
**Interaction:** drag to pan, scroll to zoom, Shift+drag (or sliders) to rotate and tilt; click a hub to focus it.

## Run it

```bash
python3 -m http.server 8000   # then open http://localhost:8000/
```
Or enable GitHub Pages (Settings → Pages → `main`, root). d3 is vendored; there is no build step.

## Data

| File | What | Updated |
|---|---|---|
| `data/states.csv` | Unemployment rate (SA), change vs. year ago, nonfarm jobs and 12-month change per state | **Automatically**, by `.github/workflows/refresh.yml` running `scripts/refresh_bls.py` against the BLS public API on the 22nd and 26th of each month (and on demand from the Actions tab) |
| `data/national.csv` | Headline tiles (unemployment, payrolls, openings, wages, recent-grad unemployment, metro breadth) | By hand after each jobs report |
| `data/hubs.csv` | The ten geospatial hubs: rank, score, OEWS cartographer jobs/wage (May 2023), rent (Oct 2026), home-price-to-wage, 2026 job signal, momentum, summary | By hand; editorial, from the research report |
| `data/metros.csv` | Metro winners/losers from the BLS metro release | By hand after each metro release |
| `data/states_geo.json` | Simplified state outlines (Albers USA, from us-atlas / Census) | Static |

Notes on the automated layer: the BLS API v1 needs no key but allows 25 requests a day; adding a free
`BLS_API_KEY` repository secret switches the script to v2 (bigger batches). The script writes the
12-month job change for every state; BLS's own release only highlights the changes it deems statistically
significant, so small figures should be read as "about flat". The initial seed (September 2026) carries
job changes only for the states BLS flagged; the first automated run fills in all 51.

## Updating the story

Chapter text and the layer definitions live at the top of the script in `index.html` (`CHAPTERS`, `LAYERS`).
Hub rankings are in `data/hubs.csv`; add or re-rank rows and the pins, list and tooltips follow.

Built from the research report "Geospatial job market geography 2026" (October 24, 2026). Not career or
investment advice.
