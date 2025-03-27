"""
DXF Drawing Library - A comprehensive library for creating and managing DXF drawings
with a focus on geometric shapes like rectangles and circles.

This library provides an object-oriented approach to creating DXF files with proper
setup for CNC and CAD applications.
"""

import ezdxf
from ezdxf.enums import TextEntityAlignment
import os
import math
from typing import List, Tuple, Dict, Optional, Union, Any


class DxfDrawing:
    """
    Main drawing class that manages the DXF document, layers, and export functionality.
    """

    def __init__(self, filename: str = "drawing.dxf", version: str = "R2010",
                 units: str = "mm", setup_layers: bool = True):
        """
        Initialize a new DXF drawing.

        Args:
            filename: Name of the DXF file to create
            version: DXF version to use (R2010 is a good modern default with broad compatibility)
            units: Drawing units ('mm', 'cm', 'in', etc.)
            setup_layers: Whether to set up default layers
        """
        # Create DXF document
        self.doc = ezdxf.new(dxfversion=version, setup=True)
        self.modelspace = self.doc.modelspace()
        self.filename = filename

        # Set up units
        self._set_units(units)

        # Dictionary to track layers
        self.layers = {}

        # Store the default layer "0" that is automatically created by ezdxf
        self.layers["0"] = self.doc.layers.get("0")

        # Create default layers if requested
        if setup_layers:
            # Layer "0" already exists, so we just need to set its properties if desired
            self.get_or_create_layer("0", color=7)  # Default layer (white)

            # Create additional layers
            self.get_or_create_layer("cut_layer", color=1)  # Red for cutting
            self.get_or_create_layer("construction", color=3, linetype="DASHED")  # Green, dashed for construction
            self.get_or_create_layer("dimension", color=5)  # Blue for dimensions

        # List to track all shapes added to the drawing
        self.shapes = []

    def _set_units(self, units: str):
        """
        Set the drawing units.

        Args:
            units: Unit type ('mm', 'cm', 'in', etc.)
        """
        # Map of unit names to ezdxf unit codes
        unit_map = {
            "mm": 4,
            "cm": 5,
            "m": 6,
            "in": 1,
            "ft": 2,
            "yd": 10
        }

        if units.lower() in unit_map:
            self.doc.header['$INSUNITS'] = unit_map[units.lower()]
            self.units = units.lower()
        else:
            # Default to mm if unit not recognized
            self.doc.header['$INSUNITS'] = 4
            self.units = "mm"

    def get_or_create_layer(self, name: str, color: int = 7, linetype: str = "CONTINUOUS",
                  lineweight: int = 25, plot: bool = True) -> str:
        """
        Get an existing layer or create a new one if it doesn't exist.

        Args:
            name: Layer name
            color: AutoCAD Color Index (ACI) color code
            linetype: Line type (CONTINUOUS, DASHED, etc.)
            lineweight: Line weight in hundredths of mm (25 = 0.25mm)
            plot: Whether the layer should be plotted/printed

        Returns:
            The name of the layer
        """
        # Check if the layer already exists
        if name in self.doc.layers:
            layer = self.doc.layers.get(name)
            # Update properties if the layer already exists
            layer.color = color
            if linetype in self.doc.linetypes:
                layer.linetype = linetype
            layer.lineweight = lineweight
            layer.plot = plot
        else:
            # Ensure the linetype exists, adding it if needed
            if linetype not in self.doc.linetypes:
                try:
                    self.doc.linetypes.add(linetype)
                except Exception:
                    # If there's an error adding the linetype, default to CONTINUOUS
                    linetype = "CONTINUOUS"

            # Create the layer
            layer = self.doc.layers.add(name)
            layer.color = color
            layer.linetype = linetype
            layer.lineweight = lineweight
            layer.plot = plot

        # Store layer in our dictionary
        self.layers[name] = layer

        return name

    # For backward compatibility
    def add_layer(self, name: str, color: int = 7, linetype: str = "CONTINUOUS",
                  lineweight: int = 25, plot: bool = True) -> str:
        """
        Add a new layer to the drawing or get an existing one.
        This is a wrapper around get_or_create_layer for backward compatibility.

        Args:
            name: Layer name
            color: AutoCAD Color Index (ACI) color code
            linetype: Line type (CONTINUOUS, DASHED, etc.)
            lineweight: Line weight in hundredths of mm (25 = 0.25mm)
            plot: Whether the layer should be plotted/printed

        Returns:
            The name of the layer
        """
        return self.get_or_create_layer(name, color, linetype, lineweight, plot)

    def save(self, filename: Optional[str] = None) -> str:
        """
        Save the drawing to a DXF file.

        Args:
            filename: Optional filename to override the default

        Returns:
            The path to the saved file
        """
        save_filename = filename if filename else self.filename

        # Ensure the file has a .dxf extension
        if not save_filename.lower().endswith('.dxf'):
            save_filename += '.dxf'

        self.doc.saveas(save_filename)
        return save_filename

    def add_shape(self, shape: 'Shape') -> None:
        """
        Add a shape to the drawing.

        Args:
            shape: A Shape object to add to the drawing
        """
        shape.add_to_drawing(self)
        self.shapes.append(shape)


class Shape:
    """
    Base class for all geometric shapes.
    """

    def __init__(self, layer: str = "0"):
        """
        Initialize a shape.

        Args:
            layer: Layer name for this shape
        """
        self.layer = layer
        self.entity = None

    def add_to_drawing(self, drawing: DxfDrawing) -> Any:
        """
        Add this shape to a drawing.

        Args:
            drawing: The DxfDrawing to add this shape to

        Returns:
            The created entity
        """
        # This method should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement add_to_drawing")

    def set_properties(self, entity: Any, **properties) -> None:
        """
        Set properties on a DXF entity.

        Args:
            entity: The DXF entity to modify
            properties: Additional properties to set
        """
        # Set basic properties
        if properties:
            for key, value in properties.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)


class Rectangle(Shape):
    """
    Rectangle shape for DXF drawings.
    """

    def __init__(self, x: float, y: float, width: float, height: float,
                 layer: str = "0", closed: bool = True, **properties):
        """
        Initialize a rectangle.

        Args:
            x: X-coordinate of bottom-left corner
            y: Y-coordinate of bottom-left corner
            width: Width of rectangle
            height: Height of rectangle
            layer: Layer name for this rectangle
            closed: Whether the polyline should be closed
            properties: Additional properties to set on the entity
        """
        super().__init__(layer)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.closed = closed
        self.properties = properties

    def add_to_drawing(self, drawing: DxfDrawing) -> Any:
        """
        Add this rectangle to a drawing.

        Args:
            drawing: The DxfDrawing to add this rectangle to

        Returns:
            The created entity
        """
        # Create the points for the rectangle
        points = [
            (self.x, self.y),                      # Bottom-left
            (self.x + self.width, self.y),         # Bottom-right
            (self.x + self.width, self.y + self.height),  # Top-right
            (self.x, self.y + self.height)         # Top-left
        ]

        # Add the LWPolyline to the modelspace
        self.entity = drawing.modelspace.add_lwpolyline(
            points,
            dxfattribs={'layer': self.layer}
        )

        # Set closed attribute
        self.entity.closed = self.closed

        # Set any additional properties
        self.set_properties(self.entity, **self.properties)

        return self.entity

    @classmethod
    def from_center(cls, center_x: float, center_y: float, width: float, height: float,
                    layer: str = "0", **properties) -> 'Rectangle':
        """
        Create a rectangle from its center point.

        Args:
            center_x: X-coordinate of center
            center_y: Y-coordinate of center
            width: Width of rectangle
            height: Height of rectangle
            layer: Layer name for this rectangle
            properties: Additional properties to set on the entity

        Returns:
            A new Rectangle object
        """
        x = center_x - width / 2
        y = center_y - height / 2
        return cls(x, y, width, height, layer, **properties)

    @classmethod
    def from_corners(cls, x1: float, y1: float, x2: float, y2: float,
                     layer: str = "0", **properties) -> 'Rectangle':
        """
        Create a rectangle from two corner points.

        Args:
            x1: X-coordinate of first corner
            y1: Y-coordinate of first corner
            x2: X-coordinate of second corner
            y2: Y-coordinate of second corner
            layer: Layer name for this rectangle
            properties: Additional properties to set on the entity

        Returns:
            A new Rectangle object
        """
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        return cls(x, y, width, height, layer, **properties)


class Circle(Shape):
    """
    Circle shape for DXF drawings.
    """

    def __init__(self, center_x: float, center_y: float, radius: float,
                 layer: str = "0", **properties):
        """
        Initialize a circle.

        Args:
            center_x: X-coordinate of center
            center_y: Y-coordinate of center
            radius: Radius of circle
            layer: Layer name for this circle
            properties: Additional properties to set on the entity
        """
        super().__init__(layer)
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.properties = properties

    def add_to_drawing(self, drawing: DxfDrawing) -> Any:
        """
        Add this circle to a drawing.

        Args:
            drawing: The DxfDrawing to add this circle to

        Returns:
            The created entity
        """
        # Add the circle to the modelspace
        self.entity = drawing.modelspace.add_circle(
            center=(self.center_x, self.center_y),
            radius=self.radius,
            dxfattribs={'layer': self.layer}
        )

        # Set any additional properties
        self.set_properties(self.entity, **self.properties)

        return self.entity

    @classmethod
    def from_diameter(cls, center_x: float, center_y: float, diameter: float,
                      layer: str = "0", **properties) -> 'Circle':
        """
        Create a circle from its center point and diameter.

        Args:
            center_x: X-coordinate of center
            center_y: Y-coordinate of center
            diameter: Diameter of circle
            layer: Layer name for this circle
            properties: Additional properties to set on the entity

        Returns:
            A new Circle object
        """
        return cls(center_x, center_y, diameter / 2, layer, **properties)

    @classmethod
    def from_three_points(cls, x1: float, y1: float, x2: float, y2: float,
                          x3: float, y3: float, layer: str = "0", **properties) -> 'Circle':
        """
        Create a circle from three points on its circumference.

        Args:
            x1, y1: Coordinates of first point
            x2, y2: Coordinates of second point
            x3, y3: Coordinates of third point
            layer: Layer name for this circle
            properties: Additional properties to set on the entity

        Returns:
            A new Circle object
        """
        # Calculate circle center and radius from three points
        # (Using the perpendicular bisector method)

        # Check if points are collinear (which would make circle impossible)
        det = (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        if abs(det) < 1e-10:
            raise ValueError("The three points are collinear and cannot form a circle")

        # Temporary variables for calculation
        A = x1 * (x1 - x3) + y1 * (y1 - y3)
        B = x2 * (x2 - x3) + y2 * (y2 - y3)

        # Calculate center
        cx = ((y2 - y3) * A - (y1 - y3) * B) / (2 * det)
        cy = ((x1 - x3) * B - (x2 - x3) * A) / (2 * det)

        # Calculate radius
        radius = math.sqrt((cx - x1) ** 2 + (cy - y1) ** 2)

        return cls(cx, cy, radius, layer, **properties)


# Utility functions for the library

def create_sample_drawing() -> DxfDrawing:
    """
    Create a sample drawing with some rectangles and circles.

    Returns:
        A DxfDrawing object with sample shapes
    """
    # Create a new drawing
    drawing = DxfDrawing("sample.dxf", units="mm")

    # Add some rectangles
    rect1 = Rectangle(10, 10, 100, 50, layer="cut_layer")
    rect1.add_to_drawing(drawing)

    rect2 = Rectangle.from_center(150, 50, 40, 40, layer="construction")
    rect2.add_to_drawing(drawing)

    # Add some circles
    circle1 = Circle(50, 100, 25, layer="cut_layer")
    circle1.add_to_drawing(drawing)

    circle2 = Circle.from_diameter(150, 100, 40, layer="dimension")
    circle2.add_to_drawing(drawing)

    return drawing


# Example usage
if __name__ == "__main__":
    # Create a new drawing
    drawing = DxfDrawing("example.dxf", units="mm")

    # Add some shapes
    rect = Rectangle(0, 0, 100, 50, layer="cut_layer")
    rect.add_to_drawing(drawing)

    circle = Circle(50, 25, 20, layer="construction")
    circle.add_to_drawing(drawing)

    # Save the drawing
    drawing.save()
    print(f"Drawing saved to {drawing.filename}")
