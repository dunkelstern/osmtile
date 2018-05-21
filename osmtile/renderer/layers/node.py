from .db import fetch_geometry
from shapely.wkb import loads


def render_node_layer(layer, clip_poly, config, image, context):
    for item in fetch_geometry(config.db, layer, clip_poly):
        geo = loads(item['geometry'], hex=True)
        print(
            layer.name,
            item[layer.text_column] if layer.text_column else item['osm_id'],
            geo
        )
