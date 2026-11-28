# Frame probes for render review

## Extract frames at exact frame numbers
Pass native Windows-style paths to ffmpeg under MSYS (for example `G:/My Drive/...`, not `/g/My Drive/...`).

```bash
VID="G:/path/to/render.mp4"
OUT="C:/path/to/review_frames"
mkdir -p "$OUT"
for f in 0 30 60 90 106 107 108 480; do
  t=$(awk "BEGIN{printf \"%.4f\", $f/30}")
  ffmpeg -nostdin -v error -ss "$t" -i "$VID" -frames:v 1 -y "$OUT/f_$(printf '%04d' $f).png"
done
```

## Labeled contact sheet
PIL, 3 columns x 4 rows, 600x338 tiles for 16:9; frame number + timecode label above each tile. For 1080x1920 vertical renders use 4 columns x 3 rows of 270x480 tiles. Use the sheet for navigation, then open individual full-resolution frames.

## Full-resolution subtitle strip
Crop `(0.12*w, 0.72*h, 0.88*w, h)` from each frame, scale to 1100 px wide, stack with frame labels. Downscaled contact-sheet tiles make Thai text unreadable; read spelling from these strips.

## Numeric zoom probe
With numpy, mask bright low-saturation pixels in a fixed upper-centre box and report BOTH bounding-box width and pixel count per frame. If the subject spans wider than the box, width saturates at the box width and is useless — use the pixel count. Stable values inside a segment and different stable values outside it identify the zoom states; a single-frame transition is an instant scale cut. Derive both plateau levels from the clip rather than hardcoding them.

On the Windows host use `py -3.13` for PIL/numpy.

## Black-border check
Concatenate the outer ~8 px strips of all four edges per sampled frame and compute the fraction of pixels whose channels are all < 20. A real letterbox gives a high fraction on the affected edge across the clip; a low maximum (a few percent) is dark background or clothing. Confirm visually before calling it FIX.

## Subtitle width and clearance
Read the widest cue from a full-resolution crop of the face-to-neck band (for vertical, x ~120..960, y ~700..1350) and check that the text sits below the chin with margins on both sides. Avoid thresholding white pixels across a broad band: hair and bokeh contaminate the measurement, including on frames with no subtitle.
