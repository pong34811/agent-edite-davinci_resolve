# Dead Ends Log

| Iteration | Approach Tried | Why It Failed | Files Touched |
|-----------|---------------|---------------|---------------|
| M2-Iter1 | V1 CropBottom=486.0, V2 CropTop=480.0, V3 Fusion Center=(0.50, 0.25) with default pivot (0.5, 0.5) | CropBottom created 964px black void in center; CropTop sliced off avatar head/face/hair; Fusion Transform pushed lower-half avatar off-screen to Y=-0.25 (83% black) | `scripts/m2_convert_pilot.py` |
