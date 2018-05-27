import colorsys


class ColorConfig:
    def __init__(self, data, defined_colors, config):
        self.color_value = self.parse_color(data, defined_colors)
        self.color_definition = data

    def __getitem__(self, key):
        if isinstance(key, int):
            if key < 4:
                return self.color_value[key]
            else:
                raise IndexError('Color has 4 components: rgb and alpha')
        elif isinstance(key, slice):
            return self.color_value[key]
        elif isinstance(key, str):
            if key.tolower() == 'r':
                return self.color_value[0]
            elif key.tolower() == 'g':
                return self.color_value[1]
            elif key.tolower() == 'b':
                return self.color_value[2]
            elif key.tolower() == 'a':
                return self.color_value[3]
            else:
                raise IndexError('Color has only 4 components: rgba')

    def __iter__(self):
        return self.color_value.__iter__()

    def serialize(self):
        return self.color_definition

    @property
    def rgb(self):
        return self.color_value[:3]

    @property
    def alpha(self):
        return self.color_value[3]

    def parse_color(self, data, defined_colors):
        if isinstance(data, list):
            if len(data) == 1:  # gray value, no alpha
                return (data[0], data[0], data[0], 1.0)
            if len(data) == 2:  # gray and alpha
                return (data[0], data[0], data[0], data[1])
            if len(data) == 3:  # rgb no alpha
                return (data[0], data[1], data[2], 1.0)
            if len(data) == 4:  # rgb with alpha
                return tuple(data)

        if isinstance(data, str):
            if data[0] == "#":  # html hex color
                r = g = b = a = 0.0
                if len(data) == 4:  # 4 bit per channel
                    r = int(data[1], base=16) / 15.0
                    g = int(data[2], base=16) / 15.0
                    b = int(data[3], base=16) / 15.0
                    a = 1.0
                if len(data) == 5:  # 4 bit per channel + alpha
                    r = int(data[1], base=16) / 15.0
                    g = int(data[2], base=16) / 15.0
                    b = int(data[3], base=16) / 15.0
                    a = int(data[3], base=16) / 15.0
                if len(data) == 7:  # 8 bit per channel
                    r = int(data[1:3], base=16) / 255.0
                    g = int(data[3:5], base=16) / 255.0
                    b = int(data[5:7], base=16) / 255.0
                    a = 1.0
                if len(data) == 9:  # 8 bit per channel + alpha
                    r = int(data[1:3], base=16) / 255.0
                    g = int(data[3:5], base=16) / 255.0
                    b = int(data[5:7], base=16) / 255.0
                    a = int(data[7:9], base=16) / 255.0
                return (r, g, b, a)
            elif data.startswith('darken('):  # darken other color
                other, amount = [x.strip() for x in data[7:-1].split(',')]
                if amount[-1] == '%':
                    amount = int(amount[:-1]) / 100.0
                else:
                    amount = int(amount)
                other_color = defined_colors.get(other)
                if other_color == None:
                    raise ValueError(
                        'Invalid color "{}", available: {}'.format(
                            other_color,
                            ", ".join(defined_colors.keys())
                        )
                    )
                tmp = list(colorsys.rgb_to_hls(*other_color[0:-1]))
                tmp[1] *= 1.0 - amount
                return (*colorsys.hls_to_rgb(*tmp), 1.0)
            elif data.startswith('lighten('):  # lighten other color
                other, amount = [x.strip() for x in data[8:-1].split(',')]
                if amount[-1] == '%':
                    amount = 1.0 + int(amount[:-1]) / 100.0
                else:
                    amount = 1.0 + float(amount)
                other_color = defined_colors.get(other)
                if other_color == None:
                    raise ValueError(
                        'Invalid color "{}", available: {}'.format(
                            other_color,
                            ", ".join(defined_colors.keys())
                        )
                    )
                tmp = list(colorsys.rgb_to_hls(*other_color[0:-1]))
                tmp[1] *= amount
                return (*colorsys.hls_to_rgb(*tmp), 1.0)
            elif data.startswith('saturation('):  # change saturation of other color
                other, amount = [x.strip() for x in data[11:-1].split(',')]
                if amount[-1] == '%':
                    amount = int(amount[:-1]) / 100.0
                else:
                    amount = int(amount)
                other_color = defined_colors.get(other)
                if other_color == None:
                    raise ValueError(
                        'Invalid color "{}", available: {}'.format(
                            other_color,
                            ", ".join(defined_colors.keys())
                        )
                    )
                tmp = list(colorsys.rgb_to_hls(*other_color[0:-1]))
                tmp[2] = amount
                return (*colorsys.hls_to_rgb(*tmp), 1.0)
            elif data.startswith('alpha('):  # change alpha of other color
                other, amount = [x.strip() for x in data[6:-1].split(',')]
                if amount[-1] == '%':
                    amount = int(amount[:-1]) / 100.0
                else:
                    amount = float(amount)

                other_color = defined_colors.get(other)
                if other_color == None:
                    raise ValueError(
                        'Invalid color "{}", available: {}'.format(
                            other_color,
                            ", ".join(defined_colors.keys())
                        )
                    )
                return (*other_color[0:-1], amount)
            else: # reference other color
                return defined_colors[data]
