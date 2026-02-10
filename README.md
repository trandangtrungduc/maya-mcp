# Maya MCP - Maya Model Context Protocol Integration

Maya MCP connects Autodesk Maya to AI assistants through the Model Context Protocol (MCP), allowing AI to directly interact with and control Maya. This integration enables AI-assisted 3D modeling, scene creation, and manipulation.

## Overview

Maya MCP is a server that bridges Maya's command port with the Model Context Protocol, enabling AI assistants like Claude to create and manipulate 3D scenes in Maya through natural language prompts.

## Features

- **Object Creation**: Create basic shapes (cube, sphere, cylinder, cone), cameras, and lights
- **Advanced Models**: Generate complex models like cars, trees, buildings, chairs, and cups
- **Material System**: Create and apply various material types (lambert, phong, blinn, metal, wood, marble, chrome, glass, etc.)
- **Scene Generation**: Generate complete scenes (city, forest, living room, office, park)
- **Curve Modeling**: Create and manipulate curves for advanced modeling
- **Mesh Operations**: Extrude, bevel, subdivide, smooth, and perform boolean operations
- **Object Management**: Duplicate, delete, rename, organize, and transform objects
- **Import/Export**: Import and export models in various formats (FBX, OBJ, USD, Alembic)
- **Third-party Integration**: Search and download models from Sketchfab and Polyhaven
- **Scene Inspection**: Get detailed information about the current scene and viewport screenshots

## Installation

### Prerequisites

- Autodesk Maya 2023 or newer
- Python 3.11 or higher
- **uv package manager**:
  - **Mac**: `brew install uv`
  - **Windows**: 
    ```powershell
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```
    Then add uv to the user path in Windows (you may need to restart your MCP client after):
    ```powershell
    $localBin = "$env:USERPROFILE\.local\bin"
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")
    ```
  - **Other platforms**: See [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- MCP-compatible AI assistant (e.g., Claude Desktop, Cursor, VSCode)

### Setup

1. **Clone or download this repository**:
   ```bash
   git clone https://github.com/trandangtrungduc/maya-mcp.git
   cd maya-mcp
   ```

2. **Configure MCP Server**:
   
   For **Cursor**, add the following to your MCP configuration file (e.g., `~/.cursor/mcp.json`):
   ```json
   {
     "mcpServers": {
       "maya": {
         "command": "uvx",
         "args": [
           "--from",
           "[PATH_TO_MAYA_MCP]",
           "maya-mcp"
         ]
       }
     }
   }
   ```
   
   Replace `[PATH_TO_MAYA_MCP]` with the actual path to your maya-mcp directory (e.g., `F:\\AI_Tools\\MCP\\maya-mcp` on Windows or `/path/to/maya-mcp` on Mac/Linux).
   
   For **Claude Desktop**, add to `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "maya-mcp": {
         "command": "uvx",
         "args": [
           "--from",
           "[PATH_TO_MAYA_MCP]",
           "maya-mcp"
         ]
       }
     }
   }
   ```
   
   Replace `[PATH_TO_MAYA_MCP]` with the actual path to your maya-mcp directory (e.g., `F:\\AI_Tools\\MCP\\maya-mcp` on Windows or `/path/to/maya-mcp` on Mac/Linux).

## Usage

Once configured, you can interact with Maya through your AI assistant using natural language prompts. The AI will automatically use the appropriate Maya MCP tools to fulfill your requests.

## Example Prompts

### Basic Object Creation

**Create a simple scene with basic shapes:**
```
Create a red cube at position (0, 0, 0), a blue sphere at (5, 0, 0), and a green cylinder at (10, 0, 0)
```

**Create lights and camera:**
```
Create a directional light pointing down at 45 degrees, a point light at (0, 10, 0), and position a camera to look at the scene
```

### Material Creation

**Create and apply materials:**
```
Create a shiny metallic material with a gold color and apply it to the cube
```

**Create procedural materials:**
```
Create a wood material with brown color and apply it to the cylinder. Then create a marble material with white base color and apply it to the sphere
```

**Create glass material:**
```
Create a transparent glass material with a slight blue tint and apply it to the sphere
```

### Advanced Models

**Create a car:**
```
Create a red sporty car at position (0, 0, 0) with a scale of 1.2
```

**Create a tree:**
```
Create an oak tree at position (5, 0, 5) with 5 branches and high leaf density
```

**Create a building:**
```
Create a building at (0, 0, 0) that is 30 units tall, 10 units wide, with 8 floors and windows on each floor
```

**Create furniture:**
```
Create a chair at position (0, 0, 0) with a seat width of 2, depth of 2, and back height of 2.5
```

### Scene Generation

**Generate a city scene:**
```
Generate a city scene with 4 blocks, high building density, and include cars on the streets
```

**Generate a forest:**
```
Generate a forest scene with 20 trees, forest size of 60 units, and include a winding path through it
```

**Generate a living room:**
```
Generate a modern living room scene with furniture, TV, and decorations
```

**Generate an office:**
```
Generate an office scene with 6 desks, each with a chair and monitor, in a modern style
```

**Generate a park:**
```
Generate a park scene with 15 trees, benches around a circular path, and a central fountain
```

### Object Manipulation

**Transform objects:**
```
Move the cube to position (5, 10, -5), rotate it 45 degrees on the Y axis, and scale it to 2x its size
```

**Duplicate objects:**
```
Duplicate the sphere 5 times, spacing them 3 units apart along the X axis
```

**Organize objects:**
```
Group all the cubes together, then arrange all spheres in a circle with radius 10
```

### Mesh Operations

**Extrude faces:**
```
Select the top face of the cube and extrude it upward by 2 units
```

**Bevel edges:**
```
Select all edges of the cube and bevel them with a width of 0.3
```

**Smooth mesh:**
```
Subdivide the sphere twice and then smooth it
```

**Boolean operations:**
```
Create a cylinder and use it to cut a hole through the cube using boolean difference
```

### Curve Modeling

**Create curves:**
```
Create a spiral curve with radius 5, height 3, and 4 turns, then create a circle curve with radius 2
```

**Model from curves:**
```
Create a profile curve in the shape of a teardrop, then create a path curve that spirals upward. Extrude the profile along the path to create a spiral object
```

**Revolve a curve:**
```
Create a profile curve for a vase shape, then revolve it 360 degrees around the Y axis to create a 3D vase
```

### Import/Export

**Import models:**
```
Import the model file "car.fbx" and place it in a namespace called "imported_car"
```

**Export scene:**
```
Export all objects in the scene to "my_scene.fbx" format
```

**Export selected:**
```
Export the currently selected objects to "selected_objects.obj"
```

### Third-party Integration

**Search Sketchfab models:**
```
Search Sketchfab for "sci-fi spaceship" models that are downloadable, limit to 10 results
```

**Download Sketchfab model:**
```
Download the Sketchfab model with UID "abc123" and scale it so the largest dimension is 5 units
```

**Search Polyhaven assets:**
```
Search Polyhaven for HDRIs in the "outdoor" category
```

**Download Polyhaven asset:**
```
Download the Polyhaven HDRI with ID "studio_small_01" at 4k resolution
```

### Scene Inspection

**Get scene information:**
```
Get detailed information about all objects, cameras, lights, and materials in the current scene
```

**Viewport screenshot:**
```
Take a screenshot of the current viewport to see what the scene looks like
```

**List objects:**
```
List all cameras in the scene, then list all lights
```

### Code Execution

**Execute Python code to understand context:**
```
Execute Python code to list all objects in the scene and print their types and positions
```

**Execute code for complex operations:**
```
Execute Python code to create a procedural grid of cubes with random heights, then apply different materials to each based on height
```

**Execute code to inspect scene state:**
```
Execute Python code to check if there are any objects with visibility turned off, and print their names
```

**Note**: The `execute_code` tool allows running arbitrary Python code in Maya, which is powerful but potentially dangerous. Always save your work before using it. The AI can use this tool automatically to understand context and perform operations that aren't covered by other tools.

### Complex Workflows

**Create a complete scene:**
```
Create a city scene with 3x3 blocks. Then add a red car in the center, create a chrome material and apply it to the car. Position a camera to look down at the city from above, and add a directional light for shadows
```

**Model a custom object:**
```
Create a cube, bevel all its edges, then extrude the top face. Create a wood material and apply it. Duplicate this object 3 times and arrange them in a row
```

**Create an animated setup:**
```
Create a sphere and a cube. Create a point light and position it between them. Create a camera and frame both objects. Apply a glass material to the sphere and a metallic material to the cube
```

## Available Tools

The Maya MCP server provides the following tools:

### Object Creation
- `create_object` - Create basic shapes, cameras, and lights
- `create_advanced_model` - Create complex models (car, tree, building, chair, cup)
- `create_curve` - Create various curve types (line, circle, spiral, helix, etc.)

### Materials
- `create_material` - Create and assign materials (lambert, phong, blinn, metal, wood, marble, chrome, glass, etc.)

### Scene Management
- `generate_scene` - Generate complete scenes (city, forest, living room, office, park)
- `scene_new` - Create a new scene
- `scene_open` - Open a scene file
- `scene_save` - Save the current scene
- `get_scene_info` - Get detailed scene information
- `get_viewport_screenshot` - Capture viewport screenshot
- `execute_code` - Execute arbitrary Python code in Maya (powerful but use with caution)

### Object Operations
- `duplicate_object` - Duplicate objects
- `delete_object` - Delete objects
- `rename_object` - Rename objects
- `set_object_transform_attributes` - Set position, rotation, scale
- `set_object_attribute` - Set any object attribute
- `get_object_attributes` - Get object attributes
- `list_objects_by_type` - List objects by type

### Organization
- `organize_objects` - Group, parent, layout, align objects
- `select_object` - Select objects
- `clear_selection_list` - Clear selection

### Modeling
- `mesh_operations` - Extrude, bevel, subdivide, smooth, boolean operations
- `curve_modeling` - Extrude, loft, revolve, sweep curves

### Import/Export
- `import_model` - Import models (FBX, OBJ, USD, Alembic)
- `export_model` - Export models in various formats

### Third-party
- `search_sketchfab_models` - Search Sketchfab
- `get_sketchfab_model_preview` - Get model preview
- `download_sketchfab_model` - Download Sketchfab model
- `search_polyhaven_assets` - Search Polyhaven
- `get_polyhaven_categories` - Get Polyhaven categories
- `download_polyhaven_asset` - Download Polyhaven assets

## Configuration

### Maya Command Port

By default, Maya MCP connects to Maya on `localhost:50007`. This is Maya's default command port. If you need to use a different port or host, you can modify the connection settings in the server code.

### Logging

The server logs all operations to `maya_mcp_server.log` in the package directory. Check this file for debugging information.

## Troubleshooting

### Connection Issues

- **Maya not responding**: Ensure Maya is running and the command port is enabled
- **Port conflicts**: Check if port 50007 is available or change it in the configuration
- **First command fails**: Sometimes the first command may not go through, but subsequent commands should work

### Tool Execution Errors

- **Object not found**: Ensure objects exist before manipulating them
- **Invalid parameters**: Check tool documentation for required parameter formats
- **Maya errors**: Check Maya's Script Editor for detailed error messages

### Performance

- **Large scenes**: Operations on scenes with many objects may take longer
- **Complex operations**: Boolean operations and mesh smoothing on high-poly objects can be slow

### Security Considerations

- **execute_code tool**: The `execute_code` tool allows running arbitrary Python code in Maya, which can be powerful but potentially dangerous. Always save your work before using it. The AI may use this tool automatically to understand context and perform complex operations.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## Acknowledgments

This project is developed from the original [MayaMCP](https://github.com/PatrickPalmer/MayaMCP) repository by Patrick Palmer. We extend our gratitude to the original author and contributors for their foundational work on the Maya Model Context Protocol integration.

## License

MIT License - see LICENSE file for details

## Author

Duc Tran (trandangtrungduc@gmail.com)

## Version

Current version: 1.1.14
