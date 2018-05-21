import argparse
from osmtile import *


parser = argparse.ArgumentParser(description='Render OSM Maps')
parser.add_argument(
    '--config',
    type=str,
    nargs=1,
    dest='config',
    required=True,
    help='Config file to use'
)
parser.add_argument(
    '--width',
    type=int,
    nargs=1,
    dest='width',
    default=2000,
    help='Width in pixels of rendered map'
)
parser.add_argument(
    '--height',
    type=int,
    nargs=1,
    dest='height',
    default=1000,
    help='Height in pixels of rendered map'
)
parser.add_argument(
    'center_lat',
    type=float,
    help='Center lattitude of map to render'
)
parser.add_argument(
    'center_lon',
    type=float,
    help='Center longitude of map to render'
)
parser.add_argument(
    'zoom',
    type=int,
    help='Zoomlevel at which to render'
)

args = parser.parse_args()

config = RenderConfig(vars(args))

image = Renderer(config).render(
    args.width,
    args.height,
    (args.center_lat, args.center_lon),
    args.zoom
)

image.write_to_png('out.png')

