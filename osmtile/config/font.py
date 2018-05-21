

class FontConfig():
    def __init__(self, data, fontdir, config):
        self.face = data.get('face', 'sans-serif')
        self.size = data.get('size', 12)
        self.style = data.get('style', 'regular')
        self.weight = data.get('weight', 400)
        if isinstance(self.weight, str):
            if self.weight == 'light':
                self.weight = 200
            elif self.weight == 'bold':
                self.weight = 800
            elif self.weight == 'black':
                self.weight = 1000
            else:
                self.weight = 400
        self.halo_size = data.get('halo_size', 0)

    def serialize(self):
        return {
            "face": self.face,
            "size": self.size,
            "style": self.style,
            "weight": self.weight,
            "halo_size": self.halo_size
        }