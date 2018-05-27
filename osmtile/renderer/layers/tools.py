
def render_polygon(context, poly):
    for idx, c in enumerate(poly.exterior.coords):
        context.line_to(c[0], c[1])
    context.close_path()

    for i in poly.interiors:
        for idx, c in enumerate(i.coords):
            if idx == 0:
                context.move_to(c[0], c[1])
            else:
                context.line_to(c[0], c[1])
        context.close_path()


def stroke_and_fill(context, style, stroke_width=0):
    if stroke_width > 0:
        context.set_source_rgba(*style.fill_color)
        context.fill_preserve()
        stroke = list(style.stroke_color)
        stroke[3] *= stroke[3]
        context.set_source_rgba(*stroke)
        context.stroke()
    else:
        context.fill()


def configure_context(context, layer, style):
    context.set_source_rgba(*style.fill_color)
    context.set_line_width(layer.stroke)

    multiplier = layer.stroke if layer.stroke > 0 else 1.0
    if style.stroke_style == 'dashed':
        context.set_dash([2.0 * multiplier, 2.0 * multiplier + multiplier])
    elif style.stroke_style == 'stippled':
        context.set_dash([1.0 * multiplier, 1.0 * multiplier + multiplier])
