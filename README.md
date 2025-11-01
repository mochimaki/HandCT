# HandCT 3D Model Pose Exporter

A Blender script to apply arbitrary poses to hand models from the HandCT dataset and export them in multiple 3D formats without requiring external add-ons.

## Features

- **Pose Application**: Apply custom finger poses to HandCT hand meshes
- **Multiple Export Formats**: Export in STL (3D printing), GLB (web sharing), or FBX (Fusion360) formats
- **No Add-ons Required**: Uses only Blender's built-in features
- **Easy Customization**: Configure finger positions with simple parameters
- **Automatic Compatibility**: Works with both Blender 3.x and 4.x versions

## Prerequisites

- **Blender 4.4.3** (or compatible version)
- **HandCT Dataset** (DOI: 10.5281/zenodo.6473101)
- Access to the `base_model.blend` file from the HandCT dataset

## Installation

1. Download or clone this repository
2. Ensure you have the HandCT dataset and the `base_model.blend` file

## Usage

### Quick Start

1. Open Blender and load the HandCT `base_model.blend` file
2. Navigate to the **Scripting** tab in Blender
3. Open the text editor and paste the contents of `arbitrary_pose.py`
4. Modify the user settings at the top of the script if needed
5. Click **Run Script** (▶) to execute

### Configuration

Edit these variables at the top of `arbitrary_pose.py`:

```python
OUT_DIR = r"C:\Temp\HandCT_02\out_pose"   # Output directory
EXPORT_FORMAT = "STL"                     # "STL" / "GLB" / "FBX"
FILENAME_BASE = "custom_pose"             # Output filename base
```

### Finger Pose Settings

Customize finger positions by modifying the `POSE` dictionary:

```python
POSE = {
    "thumb": 1.0,     # 0=closed, 1=open
    "index": 1.0,     # Index finger
    "middle": 0.1,    # Middle finger
    "ring": 1.0,      # Ring finger
    "pinky": 0.1      # Pinky finger
}
```

Each value ranges from 0.0 (closed/curled) to 1.0 (open/extended).

## Export Formats

- **STL**: For 3D printing applications (binary format)
- **GLB**: For web sharing and viewing with materials preserved
- **FBX**: For Fusion360 and other CAD software

## How It Works

1. The script locates the hand mesh with an armature modifier
2. Applies the specified finger poses to the armature bones
3. Creates a baked mesh with the applied deformation
4. Exports the resulting static mesh in the selected format

## Technical Details

- Automatically detects Blender version and uses appropriate export operators
- Compatible with Blender 3.x (`export_mesh.stl`) and 4.x (`wm.stl_export`)
- Clean temporary object handling for memory efficiency
- Error handling with detailed logging

## Notes

- Tested on Windows 11 with Blender 4.4.3
- Requires the hand mesh to have an armature modifier
- The script searches for a mesh object named "Hand Ok" or automatically detects the first mesh with an armature modifier

## Documentation

For more detailed instructions and examples, visit the [HandCT 3D Notion page](https://cubic-puffin-800.notion.site/HandCT-3D-2969b9d1b77380bb8edad00709b734d2?pvs=74).

## License

**Script**: This script (`arbitrary_pose.py`) is licensed under the MIT License. See `LICENSE` file for details.

**HandCT Dataset**: Licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). See [Zenodo record](https://zenodo.org/records/6473101) for full details (DOI: 10.5281/zenodo.6473101).

## Acknowledgments

- HandCT Dataset (DOI: 10.5281/zenodo.6473101)
- Blender community

## Contributing

Feel free to submit issues or pull requests if you encounter problems or have suggestions for improvements.
