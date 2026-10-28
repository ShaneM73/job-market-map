# US job market 2026 — 3-D map infographic

**[🗺️ Open the live 3-D map](https://shanem73.github.io/job-market-map/)** · **[📄 Read the research report](https://shanem73.github.io/job-market-map/report.html)** ([Markdown version](report/Geospatial-job-market-geography-2026.md))

**Designer and main contributor:** Prof. Xin (Shane) Miao, Missouri State University ([@ShaneM73](https://github.com/ShaneM73))

A single-page, data-driven 3-D map of the US labor market, built for geospatial-science students and
professionals. States rise and sink with the chosen measure; pins mark the ten metros where geospatial
work concentrates; four short chapters walk through the story.

**Layers:** unemployment rate · change vs. a year ago · 12-month nonfarm job growth · geospatial hubs · federal reshuffle (arcs)
**Markers:** hub pins (height = hub score, hover for the case for each), metro dots (job winners/losers)
**Interaction:** drag to pan, scroll to zoom, Shift+drag (or sliders) to rotate and tilt; click a hub pin or any relocation curve
for a standing information card at that spot (close with × or click the map). In chapters 4–5 the base map is a shaded-relief
terrain plate (Natural Earth 1:50m shaded relief + hypsometric tint, public domain, reprojected to Albers USA; `data/relief_albers.jpg`,
rebuilt with `scripts/build_relief.py`).

**Report:** the full research report behind the hub ranking is in `report/` (Markdown) and rendered as `report.html`;
the map page ends with its key findings and two charts (pay after rent by hub; core occupations vs. graduates).

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
| `data/moves.csv` | Relocations and cuts drawn as arcs/rings in chapter 5: agency, kind (growing / cutting / commercial), origin and destination, jobs, announcement date, timeline, what, why it matters for geospatial work, source URL | By hand |
| `data/occupations.csv` | BLS OOH counts for the core geospatial occupations and annual graduates | By hand (BLS OOH updates yearly) |
| `data/states_geo.json` | Simplified state outlines (Albers USA, from us-atlas / Census) | Static |
| `data/relief_albers.jpg` | Shaded-relief terrain in the same Albers USA frame (Natural Earth, public domain) | Static |

**Setup (one time):** GitHub's runners are bot-blocked by bls.gov, so the script reads the same BLS series through
FRED's official API. Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html and add it as a repository
secret named `FRED_API_KEY` (Settings → Secrets and variables → Actions). A `BLS_API_KEY` secret is optional and is tried first.
Each run writes `data/refresh_log.txt` so you can see what happened without opening the Actions logs. The script writes the
12-month job change for every state; BLS's own release only highlights the changes it deems statistically
significant, so small figures should be read as "about flat". The initial seed (September 2026) carries
job changes only for the states BLS flagged; the first automated run fills in all 51.

## Updating the story

Chapter text and the layer definitions live at the top of the script in `index.html` (`CHAPTERS`, `LAYERS`).
Hub rankings are in `data/hubs.csv`; add or re-rank rows and the pins, list and tooltips follow.

Built from the research report "Geospatial job market geography 2026" (October 24, 2026). Not career or
investment advice.
