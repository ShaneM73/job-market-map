// Inverse-project every pixel of a 2x (1950x1220) Albers-USA canvas back to lon/lat and sample the cropped rasters.
import { geoAlbersUsa } from 'd3-geo';
import fs from 'node:fs';
const proj = geoAlbersUsa().scale(1300).translate([487.5, 305]);
const S = 2, W = 975 * S, H = 610 * S;
const out = new Float64Array(W * H * 2).fill(NaN);
let n = 0;
for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const ll = proj.invert([x / S, y / S]); if (ll && isFinite(ll[0])) { out[(y * W + x) * 2] = ll[0]; out[(y * W + x) * 2 + 1] = ll[1]; n++; } }
fs.writeFileSync('lonlat.f64', Buffer.from(out.buffer)); console.log('valid', n, 'of', W * H);
