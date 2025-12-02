"""
Utility classes and functions for bit-level I/O operations.

Provides BitWriter and BitReader for writing/reading individual bits,
and functions for packing/unpacking metadata.
"""

from io import BytesIO
import struct


class BitWriter:
    """
    Write individual bits to a byte buffer.
    
    Accumulates bits and writes complete bytes to an internal buffer.
    Call flush() to write any remaining bits.
    """
    def __init__(self):
        self.buffer = BytesIO()
        self.acc = 0
        self.nbits = 0

    def write_bit(self, b):
        """Write a single bit (0 or 1)."""
        self.acc = (self.acc << 1) | (b & 1)
        self.nbits += 1
        if self.nbits == 8:
            self.buffer.write(bytes([self.acc]))
            self.acc = 0
            self.nbits = 0

    def write_bytes(self, bts: bytes):
        """Write raw bytes directly to the buffer."""
        self.buffer.write(bts)

    def flush(self):
        """Flush any remaining bits (padded with zeros)."""
        if self.nbits > 0:
            self.acc = self.acc << (8 - self.nbits)
            self.buffer.write(bytes([self.acc]))
            self.acc = 0
            self.nbits = 0

    def get_bytes(self):
        """Get all written bytes."""
        return self.buffer.getvalue()


class BitReader:
    """
    Read individual bits from a byte buffer.
    
    Reads bytes one at a time and provides access to individual bits.
    """
    def __init__(self, data: bytes):
        self.buffer = BytesIO(data)
        self.cur = 0
        self.nbits = 0

    def read_bit(self):
        """
        Read a single bit.
        
        Returns:
            int|None: 0 or 1, or None if no more data
        """
        if self.nbits == 0:
            byte = self.buffer.read(1)
            if not byte:
                return None
            self.cur = byte[0]
            self.nbits = 8
        self.nbits -= 1
        return (self.cur >> self.nbits) & 1

    def read_bytes(self, n):
        """Read n raw bytes from the buffer."""
        return self.buffer.read(n)


def pack_metadata(freqs: dict):
    """
    Pack frequency table into bytes.
    
    Format: [2 bytes: n_symbols][(1 byte symbol)(8 bytes freq) ...]
    
    Args:
        freqs (dict): Dictionary mapping byte symbols to their frequencies
        
    Returns:
        bytes: Packed metadata
    """
    n = len(freqs)
    out = bytearray()
    out.extend(struct.pack('>H', n))
    for sym, f in freqs.items():
        out.append(sym)
        out.extend(struct.pack('>Q', f))
    return bytes(out)


def unpack_metadata(bitreader: BitReader):
    """
    Unpack frequency table from bytes.
    
    Args:
        bitreader (BitReader): BitReader containing packed metadata
        
    Returns:
        tuple: (freq_dict, bytes_read)
            freq_dict maps symbols to frequencies
            bytes_read is the number of bytes consumed
            
    Raises:
        ValueError: If metadata format is invalid
    """
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

