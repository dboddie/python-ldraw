#!/usr/bin/env python

"""
ldr2svg.py - An LDraw to SVG convertor tool.

Copyright (C) 2010 David Boddie <david@boddie.org.uk>

This file is part of the ldraw Python package.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import cmdsyntax
from ldraw.geometry import Vector
from ldraw.parts import Part, Parts, PartError

try:
    from ldraw.writers.qtsvg import SVGWriter
    writer = True
except ImportError:
    writer = False

from ldraw import __version__


if __name__ == "__main__":

    syntax = "<LDraw parts file> <LDraw file> <SVG file> <viewport size> <camera position> [<look-at position>] [--sky <background colour>]"
    syntax_obj = cmdsyntax.Syntax(syntax)
    matches = syntax_obj.get_args(sys.argv[1:])
    
    if len(matches) != 1 or not writer:
        sys.stderr.write("Usage: %s %s\n\n" % (sys.argv[0], syntax))
        sys.stderr.write("ldr2svg.py (ldraw package version %s)\n" % __version__)
        sys.stderr.write("Converts the LDraw file to a SVG file.\n\n"
                         "The viewport size is specified as a pair of floating point numbers representing\n"
                         "lengths in LDraw scene coordinates separated by an \"x\" character.\n\n"
                         "The camera and look-at positions are x,y,z argument in LDraw scene coordinates\n"
                         "where each coordinate should be specified as a floating point number.\n\n"
                         "The optional sky background colour is an SVG colour, either specified as\n"
                         "#rrggbb or as a named colour.\n\n"
                         "This tool requires PyQt4, built against Qt 4.4 or higher.\n\n")
        sys.exit(1)
    
    match = matches[0]
    parts_path = match["LDraw parts file"]
    ldraw_path = match["LDraw file"]
    svg_path = match["SVG file"]
    viewport_size = map(float, match["viewport size"].split("x"))
    camera_position = Vector(*map(float, match["camera position"].split(",")))
    look_at_position = Vector(*map(float, match.get("look-at position", "0.0,0.0,0.0").split(",")))
    
    parts = Parts(parts_path)
    
    try:
        model = Part(ldraw_path)
    except PartError:
        sys.stderr.write("Failed to read LDraw file: %s\n" % ldraw_path)
        sys.exit(1)
    
    if match.has_key("sky"):
        background_colour = match["background colour"]
    else:
        background_colour = None
    
    if camera_position == look_at_position:
        sys.stderr.write("Camera and look-at positions are the same.\n")
        sys.exit(1)
    
    z_axis = (camera_position - look_at_position)
    z_axis = z_axis / abs(z_axis)
    
    up = Vector(0, -1.0, 0)
    
    x_axis = up.cross(z_axis)
    if abs(x_axis) == 0.0:
    
        up = Vector(1.0, 0, 0)
        x_axis = z_axis.cross(up)
    
    x_axis = x_axis / abs(x_axis)
    y_axis = z_axis.cross(x_axis)
    
    svg_file = open(svg_path, "w")
    writer = SVGWriter(camera_position, (x_axis, y_axis, z_axis), parts)
    writer.write(model, svg_file, viewport_size[0], viewport_size[1], background_colour = background_colour)
    svg_file.close()
    
    sys.exit()
