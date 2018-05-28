from shapely.geometry import MultiPolygon
from shapely.wkb import loads
from shapely.ops import cascaded_union, polygonize_full

from .db import fetch_geometry
from .tools import render_polygon, stroke_and_fill, configure_context

def render_line_layer(layer, clip_poly, config, image, context):
    context.save()
    style = config.styles[layer.style]

    polys = []

    for item in fetch_geometry(config.db, layer, clip_poly):
        geo = loads(item['geometry'], hex=True)
        polys.append(geo)

    if style.fuse:
        poly = cascaded_union(polys).buffer(layer.width / 2.0 + layer.stroke / 2.0)

        if not poly.is_empty:
            configure_context(context, layer, style)
            if isinstance(poly, MultiPolygon):
                for p in poly:
                    render_polygon(context, p.buffer(layer.width / 2.0 + layer.stroke / 2.0))
                    stroke_and_fill(context, style, layer.stroke)
            else:
                render_polygon(context, poly.buffer(layer.width / 2.0 + layer.stroke / 2.0))
                stroke_and_fill(context, style, layer.stroke)
    else:
        for poly in polys:
            render_polygon(context, poly.buffer(layer.width / 2.0 + layer.stroke / 2.0))
            stroke_and_fill(context, style, layer.stroke)

    context.restore()



