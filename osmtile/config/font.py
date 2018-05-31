import freetype2
FT = freetype2.FT # easier access to constants
lib = freetype2.get_default_lib()

import harfbuzz
import qahirah as qah

class FontConfig():
    def __init__(self, data, fontdir, config):
        self.ftfont = None
        self.qahfont = None
        self.hbfont = None
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
    
    def as_freetype_font(self):
        if self.ftfont is None:
            self.ftfont = lib.find_face("{face}:style={style}:weight={weight}".format(
                face=self.face.lower(),
                style=self.style.lower(),
                weight=self.weight
            ))
            self.ftfont.set_char_size(size = self.size, resolution = 90)
        return self.ftfont

    def as_qah_font(self):
        if self.qahfont is None:
            self.qahfont = qah.FontFace.create_for_ft_face(self.as_freetype_font())
        return self.qahfont

    def as_hb_font(self):
        if self.hbfont is None:
            self.hbfont = harfbuzz.Font.ft_create(self.as_freetype_font())
        return self.hbfont
