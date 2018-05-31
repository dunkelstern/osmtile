import json
import os
import psycopg2
from collections import OrderedDict

from shapely.geometry import box
from shapely.geometry.polygon import orient
from shapely.prepared import prep

from .font import FontConfig
from .icon import IconConfig
from .style import StyleConfig
from .layer import LayersConfig
from .color import ColorConfig

class RenderConfig():
    
    def __init__(self, config):
        self.occupied = []
        self.width = config.get('width', 2000)
        self.height = config.get('height', 1000)
        self.center = (
            config.get('center_lat'),
            config.get('center_lon')
        )
        self.zoom = config.get('zoom')

        # parse config file
        self.colors = {}
        self.fonts = {}
        self.icons = {}
        self.styles = {}

        self.parse_config(config.get('config')[0])

    def serialize(self):
        result = {
            "width": self.width,
            "height": self.height,
            "center": self.center,
            "zoom": self.zoom,
            "config": OrderedDict({
                "global": {
                    "min_zoom": self.minzoom,
                    "max_zoom": self.maxzoom,
                    "projection": self.projection,
                    "background": self.background,
                    "area": {
                        "xmin": self.area[0][0],
                        "ymin": self.area[0][1],
                        "xmax": self.area[1][0],
                        "ymax": self.area[1][1]
                    },
                    "database": {
                        # TODO: serialize db settings
                    }
                }
            })
        }

        result['config']['fonts'] = { key: f.serialize() for key, f in self.fonts.items() }
        result['config']['colors'] = { key: c.serialize() for key, c in self.colors.items() }
        result['config']['icons'] = { key: i.serialize() for key, i in self.icons.items() }
        result['config']['styles'] = { key: s.serialize() for key, s in self.styles.items() }
        result['config']['layers'] = self.layers.serialize()
        return result

    def serialize_json(self):
        return json.dumps(self.serialize(), indent=4)

    def parse_config(self, filename):
        config = None

        with open(filename, 'r') as fp:
            config = json.load(fp, object_pairs_hook=OrderedDict)
        
        global_conf = config.get('global')
        if global_conf is None:
            raise ValueError("Missing global section")

        self.area = [
            (global_conf.get('area').get('xmin'), global_conf.get('area').get('ymin')),
            (global_conf.get('area').get('xmax'), global_conf.get('area').get('ymax'))
        ]
        self.minzoom = global_conf.get('min_zoom', 0)
        self.maxzoom = global_conf.get('max_zoom', 22)
        self.projection = global_conf.get('projection', 'merc')
        self.background = ColorConfig(global_conf.get('background', "#ffff"), {}, self)
        self.db = self.init_db(global_conf.get('database'))

        old_cwd = os.getcwd()
        os.chdir(os.path.dirname(filename))

        # load sub-items and process includes
        for (item, constructor) in [
            ('fonts', FontConfig),
            ('colors', ColorConfig),
            ('icons', IconConfig),
            ('styles', StyleConfig),
        ]:
            # load item
            data = config.get(item, None)
            if isinstance(data, str):
                with open(data, 'r') as fp:
                    setattr(self, item, self.parse_subconf(constructor, json.load(fp, object_pairs_hook=OrderedDict)))
            elif data is not None:
                setattr(self, item, self.parse_subconf(constructor, data))
            else:
                raise ValueError('No {} section defined'.format(item))

        # load layers
        data = config.get('layers', None)
        if isinstance(data, str):
            with open(data, 'r') as fp:
                self.layers = LayersConfig(json.load(fp, object_pairs_hook=OrderedDict), self)
        elif data is not None:
            self.layers = LayersConfig(data, self)
        else:
            raise ValueError('No layers section defined')

        os.chdir(old_cwd)

    def init_db(self, db_config):
        connstring = []
        for key, value in db_config.items():
            connstring.append("{}={}".format(key, value))
        return psycopg2.connect(" ".join(connstring))
    
    def parse_subconf(self, constructor, config):
        result = {}
        for key, item in config.items():
            result[key] = constructor(item, result, self)
        return result
    
    def register_occupied(self, poly):
        # register an occupied box
        self.occupied.append(poly)

    def is_occupied(self, poly, auto_register=False):
        # prepare for multiple checking
        prepared = prep(poly)

        # filter hits
        hits = list(filter(prepared.intersects, self.occupied))
        
        # if we had no hits the area is not occupied
        if len(hits) == 0:
            if auto_register:
                # register box as occupied
                self.occupied.append(poly.buffer(20, resolution=1))
            return False
        
        # space is occupied
        return True
