from shapely.geometry import MultiPolygon

from .tools import render_polygon, stroke_and_fill, configure_context
from .db import fetch_geometry
from shapely.wkb import loads


def render_poly_layer(layer, clip_poly, config, image, context):
    context.save()
    style = config.styles[layer.style]
    configure_context(context, layer, style)

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
