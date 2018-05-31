import qahirah as qah
from qahirah import CAIRO, Colour, Matrix, Vector

from pyproj import Proj, transform
from .layers import *
import datetime

class Renderer:

    def __init__(self, config):
        self.config = config

        # HACK: de-list width and height
        if isinstance(self.config.width, list):
            self.config.width = self.config.width[0]
        if isinstance(self.config.height, list):
            self.config.height = self.config.height[0]


    def render(self, width, height, center, zoom):
        # calculate zoom and image aspect
        zoom_denominator = 2 ** zoom
        image_aspect = width / height

        # calculate render area in mercator coordinates
        full_width = abs(self.config.area[0][0]) + abs(self.config.area[1][0])
        full_height = abs(self.config.area[0][1]) + abs(self.config.area[1][1])
        render_width = full_width / zoom_denominator * image_aspect
        render_height = full_height / zoom_denominator

        mercProj = Proj(init='epsg:3857')
        latlonProj = Proj(init='epsg:4326')

        # project center lat/lon to mercator
        center_merc = transform(latlonProj, mercProj, center[1], center[0])

        # calculate clipping polygon
        poly = [
            (center_merc[0] - render_width / 2.0, center_merc[1] - render_height / 2.0),
            (center_merc[0] + render_width / 2.0, center_merc[1] - render_height / 2.0),
            (center_merc[0] + render_width / 2.0, center_merc[1] + render_height / 2.0),
            (center_merc[0] - render_width / 2.0, center_merc[1] + render_height / 2.0),
            (center_merc[0] - render_width / 2.0, center_merc[1] - render_height / 2.0),
        ]

        wkt_poly = 'POLYGON((' + ','.join([' '.join([str(x) for x in c]) for c in poly]) + '))'
        print("clipping to {}".format(wkt_poly))

        image, context = self.create_image(
            width,
            height,
            self.config.background,
            center_merc,
            (render_width, render_height)
        )

        layer_stack = self.config.layers[zoom]
        for layer in layer_stack:
            start = datetime.datetime.now()
            self.render_layer(layer, wkt_poly, image, context)
            end = datetime.datetime.now()
            print(" - Rendering layer {} took {} ms".format(layer.name, (end - start).total_seconds() * 1000.0))

        return image

    def create_image(self, width, height, background_color, center, render_size):
        # create cairo image and context
        surface = qah.ImageSurface.create(CAIRO.FORMAT_ARGB32, (width, height))
        context = qah.Context.create(surface).set_operator(CAIRO.OPERATOR_OVER)

        context.rectangle(qah.Rect(0, 0, width, height))
        context.source_colour = self.config.background.color_value
        context.fill()

        # set transform matrix for context

        # flip context
        context.translate((0, height))
        context.scale((1, -1))

        # move zero point into middle
        context.translate((-width / 2.0, -height / 2.0))
        context.scale((width, height))

        # scale to map
        context.scale((1.0 / render_size[0], 1.0 / render_size[1]))
        context.translate((-center[0] + render_size[0], -center[1] + render_size[1]))

        print(context.clip_rectangle_list)

        # default settings
        context.fill_rule = CAIRO.FILL_RULE_EVEN_ODD
        context.line_cap = CAIRO.LINE_CAP_ROUND
        context.line_join = CAIRO.LINE_JOIN_ROUND
        context.antialias = CAIRO.ANTIALIAS_GRAY

        return (surface, context)

    def render_layer(self, layer, wkt_poly, image, context):
        if layer.type == 'node':
            render_node_layer(layer, wkt_poly, self.config, image, context)
        elif layer.type == 'line':
            render_line_layer(layer, wkt_poly, self.config, image, context)
        elif layer.type == 'polygon':
            render_poly_layer(layer, wkt_poly, self.config, image, context)
