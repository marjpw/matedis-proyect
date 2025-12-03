from io import BytesIO
import struct


class BitWriter:
    def __init__(self):
        self.buffer = BytesIO()
        self.acc = 0
        self.nbits = 0

    def write_bit(self, b):
        self.acc = (self.acc << 1) | (b & 1)
        self.nbits += 1
        if self.nbits == 8:
            self.buffer.write(bytes([self.acc]))
            self.acc = 0
            self.nbits = 0

    def write_bytes(self, bts: bytes):
        self.buffer.write(bts)

    def flush(self):
        if self.nbits > 0:
            self.acc = self.acc << (8 - self.nbits)
            self.buffer.write(bytes([self.acc]))
            self.acc = 0
            self.nbits = 0

    def get_bytes(self):
        return self.buffer.getvalue()


class BitReader:
    def __init__(self, data: bytes):
        self.buffer = BytesIO(data)
        self.cur = 0
        self.nbits = 0

    def read_bit(self):
        if self.nbits == 0:
            byte = self.buffer.read(1)
            if not byte:
                return None
            self.cur = byte[0]
            self.nbits = 8
        self.nbits -= 1
        return (self.cur >> self.nbits) & 1

    def read_bytes(self, n):
        return self.buffer.read(n)


def pack_metadata(freqs: dict):
    n = len(freqs)
    out = bytearray()
    out.extend(struct.pack('>H', n))
    for sym, f in freqs.items():
        out.append(sym)
        out.extend(struct.pack('>Q', f))
    return bytes(out)


def unpack_metadata(bitreader: BitReader):
    buf = bitreader.buffer
    buf.seek(0)
    head = buf.read(2)
    if not head or len(head) < 2:
        raise ValueError("Invalid metadata: header too short")
    n = struct.unpack('>H', head)[0]
    freqs = {}
    for _ in range(n):
        sym_b = buf.read(1)
        if not sym_b:
            raise ValueError("Invalid metadata: incomplete symbol data")
        sym = sym_b[0]
        f_raw = buf.read(8)
        if len(f_raw) < 8:
            raise ValueError("Invalid metadata: incomplete frequency data")
        f = struct.unpack('>Q', f_raw)[0]
        freqs[sym] = f
    pos = buf.tell()
    bitreader.buffer.seek(pos)
    bitreader.nbits = 0
    return freqs, pos

