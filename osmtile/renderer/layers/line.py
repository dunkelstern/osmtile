from shapely.geometry import MultiPolygon
from shapely.wkb import loads
from shapely.ops import cascaded_union, polygonize_full

from .db import fetch_geometry
from .tools import render_polygon, stroke_and_fill

def render_line_layer(layer, clip_poly, config, image, context):
    context.save()
    style = config.styles[layer.style]

    context.set_line_width(layer.stroke)
    context.set_source_rgba(*style.fill_color)

    polys = []
    poly = None
    for item in fetch_geometry(config.db, layer, clip_poly):
        geo = loads(item['geometry'], hex=True)
        polys.append(geo)

    poly = cascaded_union(polys).buffer(layer.width / 2.0 + layer.stroke / 2.0)

    if not poly.is_empty:
        if isinstance(poly, MultiPolygon):
            for p in poly:
                render_polygon(context, p)
                stroke_and_fill(context, style, layer.stroke)
        else:
            render_polygon(context, poly)
            stroke_and_fill(context, style, layer.stroke)

    context.restore()



