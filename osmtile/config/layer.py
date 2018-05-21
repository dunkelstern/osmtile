import json
from collections import OrderedDict


class LayerConfig:
    LAYER_TYPES = [
        'node',
        'line',
        'polygon'
    ]

    def __init__(self, data, config):
        if isinstance(data, str):
            # load from file
            with open(data, 'r') as fp:
                data = json.load(fp, object_pairs_hook=OrderedDict)
        
        # fetch properties
        self.name = data.get('name')
        self.db_table = data.get('db_table')
        
        # type
        self.type = data.get('type', 'node')
        if self.type not in self.LAYER_TYPES:
            raise ValueError(
                'Invalid layer type "{}" in layer {}, available: {}'.format(
                    self.type,
                    self.name,
                    ", ".join(self.LAYER_TYPES)
                )
            )

        # style
        self.style = data.get('style')
        if self.style not in config.styles.keys():
            raise ValueError(
                'Invalid style name "{}", in layer {}, available: {}'.format(
                    self.style,
                    self.name,
                    ", ".join(config.styles.keys())
                )
            )
        
        # text column
        self.text_column = data.get('text_column', None)

        # type = node specific
        if self.type == 'node':
            self.icon = data.get('icon', None)
            if self.icon is not None and self.icon not in config.icons.keys():
                raise ValueError(
                    'Invalid icon "{}", in layer {}, available: {}'.format(
                        self.icon,
                        self.name,
                        ", ".join(config.icons.keys())
                    )
                )
            
        # type = polygon specific
        if self.type == 'polygon':
            self.effect3d = data.get('3d', None)
            self.stroke = data.get('stroke', 0)

        # type = line specific
        if self.type == 'line':
            self.width = data.get('width', 2)
            self.stroke = data.get('stroke', 0)
        
        # filter
        self.filter = data.get('filter', None)

    def compile_filter(self):
        if self.filter is None:
            return "True"
        result = []
        for field, filters in self.filter.items():
            for item in filters:
                result.append(
                    "{field} {op} '{value}'".format(
                        field=field,
                        op=list(item.keys())[0],
                        value=list(item.values())[0]
                    )
                )
        return ' OR '.join(result)

    def serialize(self):
        result = {
            "name": self.name,
            "db_table": self.db_table,
            "type": self.type,
            "text_column": self.text_column,
            "style": self.style,
            "filter": self.filter
        }

        if self.type == 'node':
            result['icon'] = self.icon
        elif self.type == 'line':
            result['width'] = self.width
            result['stroke'] = self.stroke
        elif self.type == 'polygon':
            result['3d'] = self.effect3d

        return result


class LayersConfig:
    def __init__(self, data, config):
        self.min_zoom = 0
        self.max_zoom = 0
        
        layers = []
        for zoomlevel, layer in data.items():

            if int(zoomlevel) > 0 and len(layers) == 0:
                # fill layer stack up with empty layers
                # until the first zoom level
                self.min_zoom = int(zoomlevel)
                layers = [[] for x in range(0, self.min_zoom)]
            if int(zoomlevel) - self.min_zoom > len(layers):
                # duplicate older layers to make a consistent
                # layer stack for all zoom levels
                for _ in range(len(layers),int(zoomlevel)):
                    layers.append(layers[-1])

            self.max_zoom = int(zoomlevel)
            if isinstance(data, str):
                # include external file
                with open(data, 'r') as fp:
                    layers.append(self.parse(json.load(fp, object_pairs_hook=OrderedDict), config))
            else:
                layers.append(self.parse(layer, config))
        
        self.layers = layers

    def __iter__(self):
        return self.layers.__iter__()

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.layers[key]
        else:
            raise TypeError("Use int values for key")

    def parse(self, data, config):
        return [LayerConfig(item, config) for item in data]

    def serialize(self):
        result = {}
        for idx, layers in enumerate(self.layers):
            result[str(idx)] = []
            for layer in layers:
                result[str(idx)].append(layer.serialize())
        return result