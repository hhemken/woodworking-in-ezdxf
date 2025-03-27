# DXF Drawing Library for Woodworking and CNC Projects

This Python library provides a user-friendly interface for creating DXF files for woodworking, CNC cutting, and other CAD applications. Built on top of the `ezdxf` package, it abstracts away the complexities of the DXF format and provides intuitive classes for creating common geometric shapes.

## Features

- Create DXF drawings with proper units (mm, inches, etc.)
- Add and manage layers with appropriate colors and line types
- Create rectangles, circles, and other shapes with simple, intuitive methods
- Support for proper DXF practices for CNC and laser cutting applications
- Example scripts for common woodworking joints

## Installation

### Prerequisites

- Python 3.6 or higher
- ezdxf library (`pip install ezdxf`)

### Basic Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/woodworking-in-ezdxf.git
   cd woodworking-in-ezdxf
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Creating a Simple Drawing

```python
from dxf_library import DxfDrawing, Rectangle, Circle

# Create a new drawing with millimeter units
drawing = DxfDrawing("my_drawing.dxf", units="mm")

# Add a rectangle
rect = Rectangle(0, 0, 100, 50, layer="cut_layer")
rect.add_to_drawing(drawing)

# Add a circle
circle = Circle(50, 25, 20, layer="construction")
circle.add_to_drawing(drawing)

# Save the drawing
drawing.save()
```

## Main Components

### DxfDrawing Class

The `DxfDrawing` class is the main entry point for creating and managing DXF files:

```python
drawing = DxfDrawing(
    filename="drawing.dxf",  # Output filename
    version="R2010",         # DXF version (R2010 is broadly compatible)
    units="mm",              # Drawing units (mm, cm, in, etc.)
    setup_layers=True        # Automatically create standard layers
)
```

#### Key Methods:

- `get_or_create_layer(name, color, linetype, lineweight, plot)`: Creates a new layer or gets an existing one
- `save(filename=None)`: Saves the drawing to a DXF file
- `add_shape(shape)`: Adds a Shape object to the drawing

### Shape Classes

#### Rectangle

Create rectangles from corners, center points, or arbitrary points:

```python
# Create from bottom-left corner
rect1 = Rectangle(x=0, y=0, width=100, height=50, layer="cut_layer")

# Create from center point
rect2 = Rectangle.from_center(center_x=50, center_y=25, width=100, height=50)

# Create from any two corner points
rect3 = Rectangle.from_corners(x1=0, y1=0, x2=100, y2=50)
```

#### Circle

Create circles using various methods:

```python
# Create from center and radius
circle1 = Circle(center_x=50, center_y=50, radius=25, layer="cut_layer")

# Create from center and diameter
circle2 = Circle.from_diameter(center_x=50, center_y=50, diameter=50)

# Create from three points on the circumference
circle3 = Circle.from_three_points(x1=0, y1=0, x2=100, y2=0, x3=50, y3=50)
```

## Example Scripts

The `examples` directory contains several ready-to-use scripts:

### Notched Rectangle (Half-Lap Joint)

Create rectangles with half-lap joints at different notch depths:

```python
python examples/notched_rectangle.py
```

This generates DXF files showing rectangles with notches at 10%, 20%, and 50% depths, suitable for creating cross-lap joints in woodworking.

## Layer Conventions

The library creates several standard layers for organization:

- `0`: Default layer (white)
- `cut_layer`: For cutting paths (red)
- `construction`: For construction/reference geometry (green, dashed)
- `dimension`: For dimensions and measurements (blue)

## Best Practices for CNC/Laser Cutting

When creating drawings for CNC or laser cutting:

1. Put all cutting paths on the `cut_layer`
2. Ensure polylines for cutting are closed (set `closed=True`)
3. Use the correct units for your machine (usually mm)
4. Avoid overlapping cut lines, which can cause double-cutting

## Extending the Library

You can easily extend this library with new shape types by subclassing the `Shape` base class:

```python
class MyCustomShape(Shape):
    def __init__(self, x, y, size, layer="0"):
        super().__init__(layer)
        self.x = x
        self.y = y
        self.size = size
    
    def add_to_drawing(self, drawing):
        # Implementation to add your custom shape to the drawing
        pass
```

## Importing Into CAD Software

The DXF files created by this library can be imported into:

- AutoCAD
- Fusion 360
- FreeCAD
- Inkscape (with DXF import plugin)
- LibreCAD
- And most other CAD software that supports the DXF format

## Troubleshooting

### Common Issues

- **Layer "0" already exists**: The library now handles this automatically by using `get_or_create_layer`
- **Text positioning**: Use the provided attributes in `dxfattribs` dictionary instead of trying to call methods on the text object
- **Path organization**: Keep all cut paths on `cut_layer` for easier CNC/laser cutting setup

## License

[MIT License](LICENSE)

## Credits

This library was built on top of the excellent [ezdxf](https://ezdxf.readthedocs.io/) package.

---

Created with love for woodworking and digital fabrication.
