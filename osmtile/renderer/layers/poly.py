import datetime

from shapely.geometry import MultiPolygon

from .text import render_text
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
        rect = context.clip_rectangle_list[0]
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
                render_poly(context, p, layer, style, stroke_width)
            for p in poly:
                render_txt(context, config, poly, item, layer, style)
        else:
            render_poly(context, poly, layer, style, stroke_width)
            render_txt(context, config, poly, item, layer, style)

    for item in fetch_geometry(config.db, layer, clip_poly):
        poly = loads(item['geometry'], hex=True)
        if isinstance(poly, MultiPolygon):
            for p in poly:
                render_txt(context, config, poly, item, layer, style)
        else:
            render_txt(context, config, poly, item, layer, style)

    end = datetime.datetime.now()
    print(' -> Drawing took {} ms'.format((end-start).total_seconds() * 1000.0))

    context.restore()


def render_poly(context, p, layer, style, stroke_width):
    if layer.expand > 0:
        render_polygon(context, p.buffer(layer.expand, resolution=2))
    else:
        render_polygon(context, p)
    stroke_and_fill(context, style, stroke_width)


def render_txt(context, config, p, item, layer, style):
    # render text
    text = item.get(layer.text_column, None)
    if text is not None and len(text) > 0:
        center = p.centroid
        render_text(context, config, style, layer, text, center)
        # print(' -> Rendering "{}" at {}, {}'.format(text, center.x, center.y))
