"""QuickXorHash, the content hash personal OneDrive returns in file.hashes.quickXorHash.

Port of the algorithm on Microsoft Learn (onedrive/developer/code-snippets/quickxorhash).
Byte n is xored into a 160-bit circular register at bit (n * 11) mod 160, and the
total length is xored little-endian into the last 8 bytes of the 20-byte digest.

Bytes whose positions are equal mod 160 land on the same bits, so they are folded
together first ("lanes"), which keeps hashing large files fast in pure Python.
"""
# REUSE_CHECKED: none in _dev repos; PyPI quickxorhash is a C extension, kept pure Python on purpose
import base64

WIDTH_BYTES = 20
WIDTH_BITS = 160
LANES = 160
SHIFT = 11
DEFAULT_CHUNK = 4 * 1024 * 1024
_MASK160 = (1 << WIDTH_BITS) - 1


def _fold_rows(buf: bytes) -> int:
    """XOR all LANES-byte rows of buf together, returned as a little-endian int."""
    rows = len(buf) // LANES
    target = 1 << (rows - 1).bit_length()
    if target > rows:
        buf += bytes((target - rows) * LANES)
    value = int.from_bytes(buf, "little")
    bits = target * LANES * 8
    while bits > LANES * 8:
        bits //= 2
        value = (value & ((1 << bits) - 1)) ^ (value >> bits)
    return value


class QuickXorHash:
    def __init__(self):
        self._lanes = 0
        self._length = 0

    def update(self, data) -> None:
        if not data:
            return
        offset = self._length % LANES
        buf = bytes(offset) + bytes(data)
        pad = -len(buf) % LANES
        if pad:
            buf += bytes(pad)
        self._lanes ^= _fold_rows(buf)
        self._length += len(data)

    def digest(self) -> bytes:
        acc = 0
        for k in range(LANES):
            byte = (self._lanes >> (8 * k)) & 0xFF
            if byte:
                shifted = byte << ((k * SHIFT) % WIDTH_BITS)
                acc ^= (shifted | (shifted >> WIDTH_BITS)) & _MASK160
        out = bytearray(acc.to_bytes(WIDTH_BYTES, "little"))
        for i, b in enumerate(self._length.to_bytes(8, "little")):
            out[WIDTH_BYTES - 8 + i] ^= b
        return bytes(out)

    def b64digest(self) -> str:
        return base64.b64encode(self.digest()).decode("ascii")


def quickxor_file(path, chunk_size: int = DEFAULT_CHUNK) -> str:
    h = QuickXorHash()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.b64digest()
