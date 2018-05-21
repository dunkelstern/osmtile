from .color import ColorConfig

class StyleConfig():
    FILL_STYLES = [
        'solid',
        'diagonally_hatched',
        'horizontally_hatched',
        'vertically_hatched',
        'stippled',
        'roughly_stippled',
        'dashed',
        'none'
    ]
    STROKE_STYLES = [
        'solid',
        'dashed',
        'stippled',
        'fanned', 
        'patterned',
        'none'
    ]

    def __init__(self, data, styledir, config):        
        # fill style
        self.fill_style = data.get('fill_style', 'solid')
        if self.fill_style not in self.FILL_STYLES:
            raise ValueError(
                'Stroke style has to be one of {}, not "{}"'.format(
                    ", ".join(self.FILL_STYLES),
                    self.fill_style
                )
            )

        # stroke style
        self.stroke_style = data.get('stroke_style', 'none')
        if self.stroke_style not in self.STROKE_STYLES:
            raise ValueError(
                'Stroke style has to be one of {}, not "{}"'.format(
                    ", ".join(self.STROKE_STYLES),
                    self.stroke_style
                )
            )
        
        # colors
        colors = [
            ('fill_color', "#000f"),
            ('stroke_color', "#0000"),
            ('text_color', "#000f"),
            ('halo_color', "#ffff")
        ]
        self.fill_color = self.stroke_color = self.text_color = self.halo_color = None
        for setting, default in colors:
            c = data.get(setting, default)
            setattr(self, setting, ColorConfig(c, config.colors, config))

        # icons
        icons = [
            ('stroke_pattern_icon', 'stroke pattern icon'),
            ('fill_pattern_icon', 'fill pattern icon'),
            ('shield_icon', 'shield icon')
        ]
        self.stroke_pattern_icon = self.fill_pattern_icon = self.shield_icon = None
        for setting, name in icons:
            setattr(self, setting, data.get(setting, None))
            if getattr(self, setting) is not None and getattr(self, setting) not in config.icons.keys():
                raise ValueError(
                    'Unkown {} "{}", defined: {}'.format(
                        name,
                        getattr(self, setting),
                        ", ".join(config.icons.keys()),
                    )
                )
    
        # stroke pattern spacing
        self.stroke_pattern_spacing = data.get('stroke_pattern_spacing', 30)
        
        # fill pattern spacing
        self.fill_pattern_spacing = data.get('fill_pattern_spacing', 100)

        # font
        self.description_font = data.get('description_font', None)
        if self.description_font is not None and self.description_font not in config.fonts.keys():
            raise ValueError(
                'Unknown font "{}", defined: {}'.format(
                    self.description_font,
                    ", ".join(config.fonts.keys())
                )
            )

    def serialize(self):
        return {
            "fill_style": self.fill_style,
            "stroke_style": self.stroke_style,
            "fill_color": self.fill_color.serialize(),
            "stroke_color": self.stroke_color.serialize(),
            "text_color": self.text_color.serialize(),
            "halo_color": self.halo_color.serialize(),
            "stroke_pattern_icon": self.stroke_pattern_icon,
            "fill_pattern_icon": self.fill_pattern_icon,
            "shield_icon": self.shield_icon,
            "stroke_pattern_spacing": self.stroke_pattern_spacing,
            "fill_pattern_spacing": self.fill_pattern_spacing,
            "description_font": self.description_font
        }
