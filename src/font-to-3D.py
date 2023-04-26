import os
import glob
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen

from svgpathtools import parse_path

def otf_to_svg(input_folder, output_folder):
    for input_otf in glob.glob(os.path.join(input_folder, "*.otf")):
        font = TTFont(input_otf)
        glyph_set = font.getGlyphSet()

        font_name = os.path.splitext(os.path.basename(input_otf))[0]
        font_output_folder = os.path.join(output_folder, font_name)
        os.makedirs(font_output_folder, exist_ok=True)

        for glyph_name in glyph_set.keys():
            glyph = glyph_set[glyph_name]
            recording_pen = RecordingPen()
            glyph.draw(recording_pen)
            
            pen = SVGPathPen(glyph_set)

            # Apply the vertical flip transformation
            transform_pen = TransformPen(pen, (1, 0, 0, -1, 0, font["head"].unitsPerEm))
            glyph.draw(transform_pen)

            svg_commands = pen.getCommands()

            # Calculate the bounding box using svgpathtools.parse_path
            path = parse_path(svg_commands)
            
            if len(path) > 0:
                bounds = path.bbox()
            else:
                bounds = (0, 0, 0, 0)

            with open(os.path.join(font_output_folder, f"{glyph_name}.svg"), "w") as svg_file:
                # Set the viewBox attribute to fit the bounding box
                svg_file.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{bounds[0]} {bounds[1]} {bounds[2] - bounds[0]} {bounds[3] - bounds[1]}">\n')
                svg_file.write(f'<path d="{svg_commands}"/>\n')
                svg_file.write("</svg>")

# Set input folder and output folder for SVG files
input_folder = "input"
output_folder = "intermediate_svgs"

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Convert all OTF files in the input folder to SVG files
otf_to_svg(input_folder, output_folder)