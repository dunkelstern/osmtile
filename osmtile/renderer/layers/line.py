import datetime
from math import sqrt, atan2, floor
from shapely.geometry import MultiPolygon, Polygon, LineString
from shapely.wkb import loads
from shapely.ops import cascaded_union, polygonize_full

from .db import fetch_geometry
from .tools import render_polygon, stroke_and_fill, configure_context
from .text import render_text

def render_line_layer(layer, clip_poly, config, image, context):
    context.save()
    style = config.styles[layer.style]

    width = layer.width
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
                width = layer.width
                stroke_width = layer.stroke

    # buffer factor is half of the desired size
    buffer = width / 2.0
    configure_context(context, layer, style)

    # load geometry
    polys = []
    for item in fetch_geometry(config.db, layer, clip_poly):
        geo = loads(item['geometry'], hex=True).simplify(scale_factor, preserve_topology=False).buffer(buffer, resolution=2, join_style=2)
        polys.append(geo)

    # fuse geometry if desired
    if style.fuse:
        start = datetime.datetime.now()
        poly = cascaded_union(polys)
        end = datetime.datetime.now()
        print(' -> Fusing took {} ms'.format((end-start).total_seconds() * 1000.0))

        start = datetime.datetime.now()
        if not poly.is_empty:
            if isinstance(poly, MultiPolygon):
                for p in poly:
                    render_polygon(context, p.buffer(buffer))
                    stroke_and_fill(context, style, stroke_width)
            else:
                render_polygon(context, poly.buffer(buffer))
                stroke_and_fill(context, style, stroke_width)
        end = datetime.datetime.now()
        print(' -> Drawing took {} ms'.format((end-start).total_seconds() * 1000.0))
    else:
        start = datetime.datetime.now()
        for poly in polys:
            render_polygon(context, poly.buffer(buffer))
            stroke_and_fill(context, style, stroke_width)
        end = datetime.datetime.now()
        print(' -> Drawing took {} ms'.format((end-start).total_seconds() * 1000.0))

    for item in fetch_geometry(config.db, layer, clip_poly):
        geo = loads(item['geometry'], hex=True)
        coords = list(geo.coords)
        idx = floor(len(coords) / 2) - 1
        center_line = LineString([coords[idx], coords[idx + 1]])

        angle = atan2(coords[idx][0] - coords[idx+1][0], coords[idx][1] - coords[idx+1][1]) + 3.1415/2.0
        if angle > 3.1415/2.0:
            angle -= 3.1415
        if angle < -3.1415/2.0:
            angle += 3.1415
        render_txt(context, config, center_line, item, layer, style, angle)

    context.restore()


def render_txt(context, config, p, item, layer, style, angle):
    # render text
    text = item.get(layer.text_column, None)
    if text is not None and len(text) > 0:
        center = p.centroid
        render_text(context, config, style, layer, text, center, rotation=angle)
        # print(' -> Rendering "{}" at {}, {}'.format(text, center.x, center.y))
