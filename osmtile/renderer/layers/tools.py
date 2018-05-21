
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
        context.set_source_rgba(*style.stroke_color)
        context.stroke()
    else:
        context.fill()
