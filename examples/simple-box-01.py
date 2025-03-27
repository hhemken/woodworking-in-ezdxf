"""
Notched Rectangle DXF Generator with 20% Width Notches

This script creates a DXF drawing of a rectangle with two notches
on each of the long sides, with notches that are 20% of the width deep.
"""

import os
import sys

# Add the parent directory to the Python path so we can import dxf_library
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Try to import our custom library
try:
    from dxf_library import DxfDrawing, Rectangle
    print(f"Successfully imported dxf_library from: {parent_dir}")
except ImportError as e:
    print(f"Error: Could not import dxf_library. {e}")
    print(f"Tried to import from: {parent_dir}")
    print("Make sure dxf_library.py is in the parent directory.")
    sys.exit(1)


def create_notched_rectangle(
    length: float = 200.0,
    width: float = 50.0,
    notch_width: float = 30.0,
    notch_depth_percentage: float = 0.2,  # Now using a percentage of width
    output_file: str = "notched_rectangle_20percent.dxf"
) -> DxfDrawing:
    """
    Create a DXF drawing of a rectangle with notches cut into the long sides.

    Args:
        length: The length of the main rectangle (along x-axis)
        width: The width of the main rectangle (along y-axis)
        notch_width: The width of each notch
        notch_depth_percentage: The depth of the notch as a percentage of width (0.2 = 20%)
        output_file: The filename for the output DXF

    Returns:
        A DxfDrawing object with the notched rectangle
    """
    # Create a new drawing with millimeter units
    drawing = DxfDrawing(output_file, units="mm")

    # Calculate positions for better centered drawing
    start_x = 0
    start_y = 0

    # Calculate actual notch depth based on percentage of width
    notch_depth = width * notch_depth_percentage

    # Calculate the positions for notches (centered on the long sides)
    notch_gap = (length - (2 * notch_width)) / 3  # Evenly space the notches

    # Create main outline rectangle
    main_rect = Rectangle(start_x, start_y, length, width, layer="cut_layer")
    main_rect.add_to_drawing(drawing)

    # Create notches on the bottom side (removing material)
    # First notch
    notch1_x = start_x + notch_gap
    notch1_y = start_y
    notch1 = Rectangle(notch1_x, notch1_y, notch_width, notch_depth, layer="cut_layer")
    notch1.add_to_drawing(drawing)

    # Second notch
    notch2_x = start_x + (2 * notch_gap) + notch_width
    notch2_y = start_y
    notch2 = Rectangle(notch2_x, notch2_y, notch_width, notch_depth, layer="cut_layer")
    notch2.add_to_drawing(drawing)

    # Create notches on the top side (removing material)
    # First notch
    notch3_x = start_x + notch_gap
    notch3_y = start_y + width - notch_depth
    notch3 = Rectangle(notch3_x, notch3_y, notch_width, notch_depth, layer="cut_layer")
    notch3.add_to_drawing(drawing)

    # Second notch
    notch4_x = start_x + (2 * notch_gap) + notch_width
    notch4_y = start_y + width - notch_depth
    notch4 = Rectangle(notch4_x, notch4_y, notch_width, notch_depth, layer="cut_layer")
    notch4.add_to_drawing(drawing)

    # Add a line showing the notch depth for visualization (at 20% from top and bottom)
    drawing.get_or_create_layer("reference_lines", color=4, linetype="DASHED")  # Cyan color

    # Add top reference line at 20% depth
    top_reference_y = start_y + width - notch_depth
    drawing.modelspace.add_line(
        start=(start_x - 10, top_reference_y),
        end=(start_x + length + 10, top_reference_y),
        dxfattribs={"layer": "reference_lines"}
    )

    # Add bottom reference line at 20% depth
    bottom_reference_y = start_y + notch_depth
    drawing.modelspace.add_line(
        start=(start_x - 10, bottom_reference_y),
        end=(start_x + length + 10, bottom_reference_y),
        dxfattribs={"layer": "reference_lines"}
    )

    # Add a dashed centerline through the middle of the board (for reference)
    centerline_y = start_y + (width / 2)
    drawing.get_or_create_layer("centerline", color=6, linetype="DASHED")  # Magenta color

    drawing.modelspace.add_line(
        start=(start_x - 10, centerline_y),  # Extend a bit beyond the rectangle
        end=(start_x + length + 10, centerline_y),
        dxfattribs={"layer": "centerline"}
    )

    # Add labels to make the drawing clearer
    drawing.get_or_create_layer("label", color=3)  # Green color

    # Add text label for the overall drawing
    text_position = (start_x, start_y + width + 15)
    title_text = f"Notched Rectangle - {int(notch_depth_percentage * 100)}% Depth Joint Example"
    text_entity = drawing.modelspace.add_text(
        title_text,
        dxfattribs={
            "layer": "label",
            "height": 5,
            "insert": text_position,
            "halign": 0,  # 0 = LEFT alignment
            "valign": 0   # 0 = BASELINE alignment
        }
    )

    # Add percentage labels for the reference lines
    depth_percent_text = f"{int(notch_depth_percentage * 100)}%"

    # Top percentage label
    drawing.modelspace.add_text(
        depth_percent_text,
        dxfattribs={
            "layer": "label",
            "height": 3.5,
            "insert": (start_x + length + 15, top_reference_y),
            "halign": 0,
            "valign": 2  # 2 = MIDDLE for vertical alignment
        }
    )

    # Bottom percentage label
    drawing.modelspace.add_text(
        depth_percent_text,
        dxfattribs={
            "layer": "label",
            "height": 3.5,
            "insert": (start_x + length + 15, bottom_reference_y),
            "halign": 0,
            "valign": 2  # 2 = MIDDLE for vertical alignment
        }
    )

    return drawing


def main():
    """Main function to create and save the notched rectangle drawing."""
    # Create the drawing with 20% notch depth
    drawing = create_notched_rectangle(notch_depth_percentage=0.2)

    # Save the drawing
    file_path = drawing.save()
    print(f"20% notched rectangle drawing saved to: {os.path.abspath(file_path)}")

    # You can also create versions with other percentages
    shallow_drawing = create_notched_rectangle(
        notch_depth_percentage=0.1,  # 10% notch depth
        output_file="notched_rectangle_10percent.dxf"
    )
    shallow_drawing.save()
    print(f"10% notched rectangle drawing saved to: notched_rectangle_10percent.dxf")

    # Create the original 50% version for comparison
    deep_drawing = create_notched_rectangle(
        notch_depth_percentage=0.5,  # 50% notch depth (original half-depth design)
        output_file="notched_rectangle_50percent.dxf"
    )
    deep_drawing.save()
    print(f"50% notched rectangle drawing saved to: notched_rectangle_50percent.dxf")


if __name__ == "__main__":
    main()