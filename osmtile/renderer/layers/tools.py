
def render_polygon(context, poly):
    for idx, c in enumerate(poly.exterior.coords):
        context.line_to((c[0], c[1]))
    context.close_path()

    for i in poly.interiors:
        for idx, c in enumerate(i.coords):
            if idx == 0:
                context.move_to((c[0], c[1]))
            else:
                context.line_to((c[0], c[1]))
        context.close_path()


def stroke_and_fill(context, style, stroke_width=0):
    if stroke_width > 0:
        if style.fill_color.alpha > 0:
            context.source_colour = style.fill_color.color_value
            context.fill_preserve()
        context.set_line_width(stroke_width)
        context.source_colour = style.stroke_color.color_value
        context.stroke()
    else:
        if style.fill_color.alpha > 0:
            context.source_colour = style.fill_color.color_value
            context.fill()


def configure_context(context, layer, style):
    multiplier = layer.stroke if layer.stroke > 0 else 1.0
    if style.stroke_style == 'dashed':
        context.set_dash(((2.0 * multiplier, 2.0 * multiplier + multiplier), 0))
    elif style.stroke_style == 'stippled':
        context.set_dash(((1.0 * multiplier, 1.0 * multiplier + multiplier), 0))
