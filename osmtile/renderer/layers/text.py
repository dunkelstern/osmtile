import harfbuzz
import qahirah as qah

from math import degrees
from shapely.geometry import Polygon

def render_text(context, config, style, layer, text, center, rotation = None):
    if style.description_font is None:
        return
    font = config.fonts[style.description_font]

    context.save()

    buffer = harfbuzz.Buffer.create()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    features = (
        harfbuzz.Feature(tag = harfbuzz.HB.TAG([ord(c) for c in 'kern']), value = 1),
        harfbuzz.Feature(tag = harfbuzz.HB.TAG([ord(c) for c in 'liga']), value = 1),
    )
    harfbuzz.shape(font.as_hb_font(), buffer, features)

    # reset context
    cliprect = context.clip_rectangle_list[0]
    matrix = context.matrix
    context.transform(matrix.inv())

    # project center into screenspace
    x = center.x - cliprect.left
    y = center.y - cliprect.top

    x *= config.width / cliprect.width
    y *= config.height / cliprect.height

    new_glyphs, endpos = buffer.get_glyphs()

    context.set_font_face(font.as_qah_font())
    context.set_font_size(font.size)
    extends = context.glyph_extents(new_glyphs)

    # attention y is flipped
    context.translate((x, config.height - y))
    if rotation is not None:
        context.rotate(rotation)
    context.translate((- extends.width / 2.0, -extends.y_bearing / 2.0))

    context.glyph_path(new_glyphs)
    path = context.copy_path().extents()

    # map boxes back to pixel space
    #mx = context.matrix.inv()
    
    mx = qah.Matrix.identity
    mx *= qah.Matrix.translate((-x, -(config.height - y)))
    if rotation is not None:
        mx *= qah.Matrix.rotate(rotation)
    mx *= qah.Matrix.translate((- extends.width / 2.0, - extends.y_bearing / 2.0))

    p1 = mx.map((path.left, path.top))
    p2 = mx.map((path.right, path.top))
    p3 = mx.map((path.right, path.bottom))
    p4 = mx.map((path.left, path.bottom))
    
    poly = Polygon([
        (-p1.x, -p1.y),
        (-p2.x, -p2.y),
        (-p3.x, -p3.y),
        (-p4.x, -p4.y),
    ])

    if not config.is_occupied(poly, auto_register=True):
        context.source_colour = style.halo_color.color_value
        context.line_width = font.halo_size * 2
        context.stroke()

        context.source_colour = style.text_color.color_value
        context.show_glyphs(new_glyphs)
    else:
        context.new_path()


    # # calculate bounding box in pixel space
    # topleft = context.device_to_user(path.topleft)
    # bottomright = context.device_to_user(path.botright)



    # topleft.x *= -1
    # topleft.y *= -1
    # bottomright.x *= -1
    # bottomright.y *= -1

    # print(topleft, bottomright)
    # if not config.is_occupied(topleft, bottomright, auto_register=True):
    #     context.source_colour = style.halo_color.color_value
    #     context.line_width = font.halo_size * 2
    #     context.stroke()

    #     context.source_colour = style.text_color.color_value
    #     context.show_glyphs(new_glyphs)
    # else:
    #     print("  <> Space occupied")
    #     context.new_path()
    
    context.restore()

    # context.save()

    # context.transform(matrix.inv())
    
    # context.move_to((-p1.x, - p1.y))
    # context.line_to((-p2.x, - p2.y))
    # context.line_to((-p3.x, - p3.y))
    # context.line_to((-p4.x, - p4.y))
    # context.close_path()

    # context.line_width = 1
    # context.source_colour = (1.0, 0.0, 0.0, 1.0)
    # context.stroke()

    # context.restore()
