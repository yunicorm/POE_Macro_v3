# Tincture Template Images

This directory contains template images for Tincture icon detection.

## File Naming Convention

Template images should be named according to the following pattern:
```
{tincture_name}_{resolution}.png
```

## Required Template Images

### Sap of the Seasons
- `sap_of_the_seasons_1920x1080.png` - For 1920x1080 resolution
- `sap_of_the_seasons_2560x1440.png` - For 2560x1440 resolution  
- `sap_of_the_seasons_3840x2160.png` - For 3840x2160 resolution

## Image Requirements

- **Format**: PNG (preferred for transparency support)
- **Color Space**: BGR (OpenCV standard)
- **Size**: Should match the actual size of the UI element in the game
- **Quality**: High quality screenshots without compression artifacts

## Capture Guidelines

1. Take screenshots at native resolution
2. Crop to include only the tincture icon area
3. Ensure consistent lighting and UI state
4. Save as PNG to preserve quality

## Usage Notes

- The TinctureDetector will automatically select the appropriate template based on detected screen resolution
- Templates are cached in memory for performance
- Missing templates will cause initialization errors