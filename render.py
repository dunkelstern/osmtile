import argparse
import datetime
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
    default=[2000],
    help='Width in pixels of rendered map'
)
parser.add_argument(
    '--height',
    type=int,
    nargs=1,
    dest='height',
    default=[1000],
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

start = datetime.datetime.now()
config = RenderConfig(vars(args))
end = datetime.datetime.now()
print("Parsing config took {} ms".format((end-start).total_seconds() * 1000.0))

start = datetime.datetime.now()
image = Renderer(config).render(
    args.width[0],
    args.height[0],
    (args.center_lat, args.center_lon),
    args.zoom
)
end = datetime.datetime.now()
print("Rendering took {} ms".format((end-start).total_seconds() * 1000.0))

image.write_to_png('out.png')

