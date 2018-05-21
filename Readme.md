# OSMTile

Python implementation for a OSM Map-Renderer

## Quick and dirty how-to

1. Create a PostgreSQL Database with PostGIS activated
2. Fetch a copy of [imposm3](https://github.com/omniscale/imposm3)
3. Get a OpenStreetMap data file (for example from [Geofabrik](http://download.geofabrik.de/), start with a small region!)
4. Import some OpenStreetMap data into the DB:
```bash
$ imposm import -connection postgis://user:password@host:port/database -mapping doc/imposm_mapping.yml -read /path/to/osm.pbf -write -deployproduction
```
5. Create a virtualenv and install packages:
```bash
mkvirtualenv -p /usr/bin/python3 osmtile
pip install -r requirements.txt
```
6. Render a map:
```bash
python render.py --config config/config.json 48.3849 10.8631 14
```

## Layer config

### Global

Global configuration for the map

Example:

```json
{
    "global": {
        "background": "#f0f0f0",
        "projection": "merc",
        "min_zoom": 0,
        "max_zoom": 22,
        "area": {
            "xmin": -20037508.34,
            "ymin": -20037508.34,
            "xmax": 20037508.34,
            "ymax": 20037508.34
        },
        "database": {
            "user": "osm",
            "dbname": "osm"
        }
    }
}
```

- `minzoom` Minimal zoom level (usually 0, fit the world into viewport)
- `maxzoom` Maximal zoom level (usually 22, displays full detail)
- `projection` usually `merc` for spherical mercator
- `area` Mapping area in projected coordinates
    - `xmin`
    - `ymin`
    - `xmax`
    - `ymax`
- `database`
    - `user`
    - `password`
    - `dbame`
    - `hostname`
    - `port`
- `background` background color

### Definitions

#### Fonts

Example:

```json
{
    "fonts": {
        "country": {
            "face": "DejaVu Sans",
            "size": 50,
            "style": "regular",
            "weight": 800,
            "halo_size": 3
        },
        "road": {
            "face": "DejaVu Sans",
            "size": 14,
            "style": "regular",
            "weight": 400,
            "halo_size": 1
        }
    }
}
```

- Dict: key = short Name or string (filename) or array (list of filenames)
- Value: Dict
    - face
    - size
    - style (regular, italic)
    - weight
    - halo size

#### Colors

Example:

```json
{
    "colors": {
        "road_residential": [0.8, 0.8, 0.8, 1.0],
        "road_motorway": [0.8, 0.8, 0.0, 1.0],
        "forest": [0.3, 0.9, 0.3, 1.0],
        "moor": [0.3, 0.3, 0.0, 1.0]
    }
}
```

- Dict: key = short Name or string (filename) or array (list of filenames)
- Value one of: 
    - Array [r, g, b, a]
    - HTML Hex color: `#rrggbbaa`, shorthands allowed: `#rgb`.
      If alpha is skipped it is assumed as 1.0/fully opaque
    - Function:
        - `darken(<color>, <percentage>)`
        - `lighten(<color>, <percentage>)`
        - `saturation(<color>, <percentage>)`
        - `alpha(<color>, <percentage>)`

#### Icons

Example:

```json
{
    "icons": {
        "forest": {
            "filename": "img/tree@2x.png",
            "colorize": "darken(forest, 20%)",
            "scale": 0.5
        },
        "moor": {
            "derive": "forest",
            "colorize": "moor"
        },
        "motorway": {
            "filename": "img/motorway@2x.png",
            "scale": 0.5,
            "split_positions": [5, 5]
        }
    }
}
```

- Dict: key = short Name or string (filename) or array (list of filenames)
- Value: Dict
    - `filename` (load from file, png or svg)
    - `derive` (derive from other icon)
    - `colorize` (use only alpha of icon and apply color or function)
    - `scale` (scale the image, used for @2x icons to facilitate retina rendering)
    - `split_positions` array of two pixel positions where to split the icon to fit text if used as shield, second value is pixels from the right boundary

#### Styles

Example:

```json
{
    "styles": {
        "road_residential": {
            "fill_color": "road_residential",
            "stroke_color": "darken(road_residential, 20%)",
            "description_font": "road",
            "text_color": "darken(road_residential, 20%)",
            "halo_color": [1.0, 1.0, 1.0, 1.0]
        },
        "road_motorway": {
            "fill_color": "road_motorway",
            "stroke_color": "darken(road_motorway, 20%)",
            "description_font": "road",
            "text_color": "darken(road_motorway, 20%)",
            "halo_color": [1.0, 1.0, 1.0, 1.0],
            "shield_icon": "motorway"
        },
        "forest": {
            "fill_color": "forest",
            "font": "road",
            "text_color": "darken(forest, 20%)",
            "halo_color": "lighten(forest, 20%)",
            "fill_pattern_icon": "forest",
            "fill_pattern_spacing": 30
        }
    }
}
```

Value: Dict key = short name or string (filename) or array (list of filenames)

- `fill_color` polygon or line stroke fill color
- `stroke_color` polygon outline or stroke outline color
- `description_font` font to use for text
- `text_color`
- `halo_color` Text outline halo color to use
- `fill_pattern_icon` Fill the polygon with a sparse fill of this icon
- `fill_pattern_spacing` Pixels between renditions of the pattern icons
- `fill_style` one of `solid`, `diagonally_hatched`, `horizontally_hatched`, `vertically_hatched`, `stippled`, `roughly_stippled`, `dashed` or `none`, defaults to `solid`
- `stroke_style` one of `solid`, `dashed`, `stippled`, `fanned`, `patterned`
- `stroke_pattern_icon` icon to repeat on the stroke line if `patterned` has been selected
- `stroke_pattern_spacing` spacing in pixels between renditions of the pattern icons
- `shield_icon` render icon behind description text

### Zoomlevels

```json
{ 
    "layers": {
        "12": [
            {
                "name": "Forests",
                "db_table": "areas",
                "type": "polygon",
                "style": "forest",
                "filter": {
                    "designation": [
                        { "=": "forest" }
                    ]
                }
            },
            {
                "name": "Roads",
                "db_table": "roads",
                "type": "line",
                "text_column": "name",
                "style": "road_residential",
                "width": 5,
                "stroke": 1
            }, 
            {
                "name": "Motorways",
                "db_table": "motorways",
                "type": "line",
                "text_column": "name",
                "style": "road_motorway",
                "width": 9,
                "stroke": 2
            }
        ]
    } 
}
```

- You can skip layers that will have the same config as a previous one.
- You have to define the first zoom level you want to support and the last one (even if the last is a duplicate)

Dict: key = level
Value: array (see below) or string (filename)

#### Layer definition

If array item is a string then it defines a file to load,
if it is a dict the layer definition is inline 

- `name`
- `db_table`
- `type` one of 
    - `node` (renders icons),
    - `polygon` (renders polygons),
    - `line` (renders lines of constant width)
- `text_column`
- `style`

##### Node type

- `icon`

##### Polygon type

- `3d` make pseudo 3d shapes for buildings, bigger values are bigger effect
- `stroke` stroke width in pixels

##### Line type

- `width` width in pixels
- `stroke` stroke width in pixels

##### Filter

Array of Dicts

- Key: db field
- Value: Array of dict (or choices)
    - Key: operator (`=`, `<=`, `>=`, `<`, `>`, `!=`)
    - Value: operator value

