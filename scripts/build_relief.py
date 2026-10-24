#!/usr/bin/env python3
"""Rebuild data/relief_albers.jpg from Natural Earth 1:50m rasters (public domain).

1. Get HYP_50M_SR_W.tif and SR_50M.tif (naturalearthdata.com, or the nvkelso/natural-earth-raster GitHub mirror).
2. Crop both to lon -180..-60, lat 15..75 and save as hyp_us.png / sr_us.png.
3. node reproject_relief.mjs  -> lonlat.f64 (inverse Albers USA lon/lat for every pixel of a 1950x1220 canvas; needs d3-geo).
4. Run this script in the same folder: samples the rasters at those coordinates, blends tint + shade, writes the JPEG.
"""
import numpy as np
from PIL import Image
W, H = 1950, 1220
ll = np.fromfile('lonlat.f64', dtype=np.float64).reshape(H, W, 2)
hyp = np.array(Image.open('hyp_us.png')); sr = np.array(Image.open('sr_us.png'))
px = 1 / 0.03333333333333
col = np.clip(((ll[..., 0] + 179.98333333333333) * px).astype(int), 0, hyp.shape[1] - 1)
row = np.clip((((89.98333333333333 - ll[..., 1]) * px) - int((89.98333333333333 - 75) * px)).astype(int), 0, hyp.shape[0] - 1)
rgb = hyp[row, col].astype(float); shade = sr[row, col].astype(float)[..., None]
img = 0.5 * rgb + 0.5 * np.repeat(shade, 3, -1); img = img * 0.92 + 255 * 0.08
Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save('relief_albers.jpg', quality=86, optimize=True)
