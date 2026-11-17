"""Read NBT resources without starting Minecraft or Java (standard library only)."""
import gzip
import io
import struct


class Reader:
    def __init__(self, raw):
        self.stream = io.BytesIO(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)

    def number(self, fmt):
        return struct.unpack('>' + fmt, self.stream.read(struct.calcsize('>' + fmt)))[0]

    def string(self):
        # Modified UTF-8 NUL is legal in NBT. Resource identifiers are ASCII.
        return self.stream.read(self.number('H')).replace(b'\xc0\x80', b'\x00').decode('utf-8', 'surrogatepass')

    def payload(self, tag):
        if tag in (1, 2, 3, 4, 5, 6):
            return self.number({1:'b', 2:'h', 3:'i', 4:'q', 5:'f', 6:'d'}[tag])
        if tag == 7:
            return self.stream.read(self.number('i'))
        if tag == 8:
            return self.string()
        if tag == 9:
            subtype, length = self.number('B'), self.number('i')
            if length < 0:
                raise ValueError('Negative list length')
            return [self.payload(subtype) for _ in range(length)]
        if tag == 10:
            value = {}
            while True:
                subtype = self.number('B')
                if not subtype:
                    return value
                name = self.string()
                value[name] = self.payload(subtype)
        if tag in (11, 12):
            length = self.number('i')
            return [self.number('i' if tag == 11 else 'q') for _ in range(length)]
        raise ValueError('Unsupported NBT tag ' + str(tag))

    def root(self):
        tag = self.number('B')
        if tag != 10:
            raise ValueError('Expected compound root')
        self.string()
        value = self.payload(tag)
        if self.stream.read(1):
            raise ValueError('Trailing NBT data')
        return value


def read(raw):
    return Reader(raw).root()
