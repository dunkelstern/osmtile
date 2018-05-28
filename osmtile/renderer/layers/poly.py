from shapely.geometry import MultiPolygon

from .tools import render_polygon, stroke_and_fill, configure_context
from .db import fetch_geometry
from shapely.wkb import loads


def render_poly_layer(layer, clip_poly, config, image, context):
    context.save()
    style = config.styles[layer.style]
    configure_context(context, layer, style)

    # FIXME: probably fuse

    stroke_width = layer.stroke

    # if the layer has a minimum pixel width, scale the size to meet that
    if layer.min_pixel_width is not None:
        matrix = context.get_matrix()
        matrix.invert()

        # magic, FIXME: check if this works on complete globe
        scale_factor = matrix.xx * (0.09 - 0.005 * config.zoom) * config.zoom / 2.0

        # we only upscale
        if scale_factor > 1.0:
            stroke_width *= sqrt(matrix.xx)
    
    for item in fetch_geometry(config.db, layer, clip_poly):
        poly = loads(item['geometry'], hex=True)
        if isinstance(poly, MultiPolygon):
            for p in poly:
                if layer.expand > 0:
                    render_polygon(context, p.buffer(layer.expand))
                else:
                    render_polygon(context, p)
                stroke_and_fill(context, style, stroke_width)
        else:
            if layer.expand > 0:
                render_polygon(context, poly.buffer(layer.expand))
            else:
                render_polygon(context, poly)
            stroke_and_fill(context, style, stroke_width)

    context.restore()
