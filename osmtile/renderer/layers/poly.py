import datetime

from shapely.geometry import MultiPolygon

from .tools import render_polygon, stroke_and_fill, configure_context
from .db import fetch_geometry
from shapely.wkb import loads


def render_poly_layer(layer, clip_poly, config, image, context):
    context.save()
    style = config.styles[layer.style]

    # FIXME: probably fuse

    stroke_width = layer.stroke

    # if the layer has a minimum pixel width, scale the size to meet that
    scale_factor = 1.0
    if layer.min_pixel_width is not None:
        matrix = context.get_matrix()
        matrix.invert()

        rect = context.copy_clip_rectangle_list()[0]
        scale_factor = rect.width / config.width

        # we only upscale
        if scale_factor > 1.0:
            width = scale_factor * layer.min_pixel_width
            aspect = layer.stroke / layer.width
            stroke_width = aspect * width
            if width < layer.width:
                stroke_width = layer.stroke

    configure_context(context, layer, style)

    start = datetime.datetime.now()
    for item in fetch_geometry(config.db, layer, clip_poly):
        poly = loads(item['geometry'], hex=True).simplify(scale_factor)
        if isinstance(poly, MultiPolygon):
            for p in poly:
                if layer.expand > 0:
                    render_polygon(context, p.buffer(layer.expand, resolution=2))
                else:
                    render_polygon(context, p)
                stroke_and_fill(context, style, stroke_width)
        else:
            if layer.expand > 0:
                render_polygon(context, poly.buffer(layer.expand, resolution=2))
            else:
                render_polygon(context, poly)
            stroke_and_fill(context, style, stroke_width)
    end = datetime.datetime.now()
    print(' -> Drawing took {} ms'.format((end-start).total_seconds() * 1000.0))

    context.restore()
