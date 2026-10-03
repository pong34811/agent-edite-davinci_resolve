"""Inspect Katy404 facial and controller features in rendered still."""
from PIL import Image
import numpy as np

# Load still with Tilt -80
im = Image.open("test_qc_stills/split_pan936_tilt80.png")
arr = np.array(im)

# Let's inspect the lower half: rows 960 to 1920, cols 0 to 1080
# Find where face/skin color is: skin color typically R > 150, G > 100, B > 100, R > G > B
skin_mask = (arr[:, :, 0] > 180) & (arr[:, :, 1] > 140) & (arr[:, :, 2] > 130) & (arr[:, :, 0] > arr[:, :, 1]) & (arr[:, :, 1] > arr[:, :, 2])
# Controller color: purple/violet typically R > 80, B > 100, B > G, R > G
purple_mask = (arr[:, :, 2] > 100) & (arr[:, :, 0] > 80) & (arr[:, :, 2] > arr[:, :, 1] * 1.3) & (arr[:, :, 0] > arr[:, :, 1] * 1.1)

for name, mask in [("Skin/Face", skin_mask), ("Purple Controller", purple_mask)]:
    # lower half only
    rows, cols = np.where(mask[960:, :])
    if len(rows) > 0:
        rows = rows + 960
        print(f"[{name}] Detected {len(rows)} pixels! Row range: {rows.min()}..{rows.max()}, Col range: {cols.min()}..{cols.max()}")
        print(f"  Center: row {rows.mean():.1f}, col {cols.mean():.1f}")
    else:
        print(f"[{name}] No pixels detected!")

# Print avatar headroom: gap between split midline (960) and top of avatar
# Check first row below 960 where avatar appears
for r in range(960, 1400):
    row_pixels = arr[r, :, :]
    # Check if there is non-black content in this row
    if (row_pixels.mean(axis=1) > 10.0).any():
        print(f"First non-black avatar row: {r} (headroom below midline 960 = {r - 960} px)")
        break
