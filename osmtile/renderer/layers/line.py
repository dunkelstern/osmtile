from math import sqrt
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

    width = layer.width
    stroke_width = layer.stroke

    # if the layer has a minimum pixel width, scale the size to meet that
    if layer.min_pixel_width is not None:
        matrix = context.get_matrix()
        matrix.invert()

        # magic, FIXME: check if this works on complete globe
        scale_factor = matrix.xx * (0.09 - 0.005 * config.zoom) * config.zoom / 2.0
        # we only upscale
        if scale_factor > 1.0:
            stroke_width *= scale_factor
            width *= scale_factor
    
    # buffer factor is half of the desired size
    buffer = width / 2.0 + stroke_width / 2.0

    if style.fuse:
        poly = cascaded_union(polys).buffer(buffer)

        if not poly.is_empty:
            configure_context(context, layer, style)
            if isinstance(poly, MultiPolygon):
                for p in poly:
                    render_polygon(context, p.buffer(buffer))
                    stroke_and_fill(context, style, stroke_width)
            else:
                render_polygon(context, poly.buffer(buffer))
                stroke_and_fill(context, style, stroke_width)
    else:
        for poly in polys:
            render_polygon(context, poly.buffer(buffer))
            stroke_and_fill(context, style, stroke_width)

    context.restore()



