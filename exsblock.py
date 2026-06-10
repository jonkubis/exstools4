# ███████╗██╗  ██╗███████╗██████╗ ██╗      ██████╗  ██████╗██╗  ██╗   ██████╗ ██╗   ██╗
# ██╔════╝╚██╗██╔╝██╔════╝██╔══██╗██║     ██╔═══██╗██╔════╝██║ ██╔╝   ██╔══██╗╚██╗ ██╔╝
# █████╗   ╚███╔╝ ███████╗██████╔╝██║     ██║   ██║██║     █████╔╝    ██████╔╝ ╚████╔╝
# ██╔══╝   ██╔██╗ ╚════██║██╔══██╗██║     ██║   ██║██║     ██╔═██╗    ██╔══██╗  ╚██╔╝
# ███████╗██╔╝ ██╗███████║██████╔╝███████╗╚██████╔╝╚██████╗██║  ██╗██╗██████╔╝   ██║
# ╚══════╝╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚═╝╚═════╝    ╚═╝
"""
Low-level reader for the 84-byte header that wraps every chunk ("block") in an
EXS24 file. Inspired by the block model in Jürgen Moßgraber's ConvertWithMoss,
this is what lets us read **both** byte orders that Logic writes in the wild.

Each block on disk looks like::

    offset  size  field
    ------  ----  ------------------------------------------------------------
       0      1   byte order: 0x00 = big-endian, otherwise little-endian
       1      1   version major (always 1)
       2      1   version minor (always 0)
       3      1   block type; low nibble is the real type, high bits are flags
       4      4   content size (uint32, byte-order per byte 0)
       8      4   index        (uint32)
      12      4   flags        (uint32)
      16      4   magic word (TBOS/JBOS little-endian, SOBT/SOBJ big-endian)
      20     64   name (NUL-terminated ASCII)
      84   size   content
"""
import struct

# Block types (the *low nibble* of the type byte at offset 3).
# Core block types we read and write.
TYPE_INSTRUMENT = 0x00
TYPE_ZONE = 0x01
TYPE_GROUP = 0x02
TYPE_SAMPLE = 0x03
TYPE_PARAMS = 0x04

# Auxiliary blocks that occur in real files but which we do not interpret. A
# census of the factory library turned up types 0x05-0x0B: assorted drum-kit
# metadata, 4-byte zero padding (0x08), and two binary-plist blocks. They are
# skipped on read; the writer never emits them. Anything outside this range is
# reported as genuinely unknown.
TYPE_BPLIST_SAMPLER_LAYOUT = 0x0A   # binary plist: Sampler's layout config
TYPE_BPLIST_MACOS_PLIST = 0x0B      # binary plist: macOS info about the samples
SKIPPABLE_TYPES = (0x05, 0x06, 0x07, 0x08, 0x09, TYPE_BPLIST_SAMPLER_LAYOUT,
                   TYPE_BPLIST_MACOS_PLIST)

# The four magic words. The first header byte selects the byte order, and the
# magic must agree with it.
BIG_ENDIAN_MAGICS = (b"SOBT", b"SOBJ")
LITTLE_ENDIAN_MAGICS = (b"TBOS", b"JBOS")

HEADER_SIZE = 84


class EXSBlock:
    """One parsed EXS24 chunk header plus its raw content.

    Attributes
    ----------
    type : int
        The block type, masked to its low nibble (see ``TYPE_*``).
    name : str
        The 64-byte block name with the trailing NULs stripped.
    index : int
        The block index as stored in the header.
    content : bytes
        Just the content bytes (``size`` long), without the header.
    is_big_endian : bool
        True if the numeric fields are big-endian.
    offset : int
        Byte offset of this block's start within the source file.
    legacy_data : bytes
        ``content`` prefixed by the 76 header bytes that follow the size field
        (index + flags + magic + name). This is exactly what the original
        ``parse_*`` functions expect, and what the writer's ``original_*_data``
        pass-through replays, so it is preserved for compatibility.
    """

    __slots__ = ("type", "name", "index", "content", "is_big_endian", "offset",
                 "legacy_data")

    def __init__(self, type, name="", index=0, content=b"", is_big_endian=False,
                 offset=0, legacy_data=b""):
        self.type = type
        self.name = name
        self.index = index
        self.content = content
        self.is_big_endian = is_big_endian
        self.offset = offset
        self.legacy_data = legacy_data

    @property
    def endian(self):
        """The :mod:`struct` byte-order prefix for this block's numbers."""
        return ">" if self.is_big_endian else "<"

    @classmethod
    def parse(cls, data, offset):
        """Parse one block out of ``data`` starting at ``offset``.

        Returns ``(block, next_offset)``. Raises ``ValueError`` if the header is
        not a recognizable EXS block (bad version or magic).
        """
        if offset + HEADER_SIZE > len(data):
            raise ValueError(f"Truncated EXS block header at offset {offset}")

        is_big_endian = data[offset] == 0x00
        version_major, version_minor = data[offset + 1], data[offset + 2]
        if version_major != 1 and version_minor != 0:
            raise ValueError(
                f"Unknown EXS block version {version_major}.{version_minor} "
                f"at offset {offset}")

        # The high bits of the type byte are flags (0x40 and 0x80 occur in the
        # wild); the real type is the low nibble.
        block_type = data[offset + 3] & 0x0F

        endian = ">" if is_big_endian else "<"
        size, index = struct.unpack_from(endian + "II", data, offset + 4)
        # (the uint32 of flags at offset+12 is read as part of legacy_data below)

        magic = bytes(data[offset + 16:offset + 20])
        valid_magics = BIG_ENDIAN_MAGICS if is_big_endian else LITTLE_ENDIAN_MAGICS
        if magic not in valid_magics:
            raise ValueError(f"Unknown EXS magic {magic!r} at offset {offset}")

        name = data[offset + 20:offset + 84].split(b"\x00", 1)[0].decode("latin-1")

        end = offset + HEADER_SIZE + size
        content = data[offset + HEADER_SIZE:end]
        legacy_data = data[offset + 8:end]  # index + flags + magic + name + content

        block = cls(block_type, name, index, content, is_big_endian, offset,
                    legacy_data)
        return block, end


def iter_blocks(data):
    """Yield every :class:`EXSBlock` in ``data`` in file order."""
    offset = 0
    n = len(data)
    while offset < n:
        block, next_offset = EXSBlock.parse(data, offset)
        if next_offset <= offset:
            raise ValueError(f"EXS block made no progress at offset {offset}")
        yield block
        offset = next_offset
