from shapely.geometry import MultiPolygon

from renderer.layers.tools import render_polygon, stroke_and_fill
from .db import fetch_geometry
from shapely.wkb import loads


def render_poly_layer(layer, clip_poly, config, image, context):
    context.save()
    style = config.styles[layer.style]

    context.set_source_rgba(*style.fill_color)
    context.set_line_width(layer.stroke)

    for item in fetch_geometry(config.db, layer, clip_poly):
        poly = loads(item['geometry'], hex=True)
        if isinstance(poly, MultiPolygon):
            for p in poly:
                render_polygon(context, p)
                stroke_and_fill(context, style, layer.stroke)
        else:
            render_polygon(context, poly)
            stroke_and_fill(context, style, layer.stroke)

    context.restore()
