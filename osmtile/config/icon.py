from .color import ColorConfig

class IconConfig():
    def __init__(self, data, icondir, config):
        self.filename = data.get('filename')
        self.colorize = data.get('colorize', None)
        if self.colorize is not None:
            self.colorize = ColorConfig(self.colorize, config.colors, config)
        self.scale = data.get('scale', 1.0)
        self.split_positions = data.get('split_positions', [0, 0])

    def image(self):
        # TODO: load from file and colorize when needed
        pass
    
    def serialize(self):
        return {
            "filename": self.filename,
            "colorize": self.colorize.serialize() if self.colorize is not None else None,
            "scale": self.scale,
            "split_positions": self.split_positions
        }