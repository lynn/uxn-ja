from dataclasses import dataclass
from typing import *
import sys


@dataclass
class Glyph:
    """A glyph read from a BDF file.

    Attributes:
        width (int): The width in pixels (8 or 16).
        height (int): The height in pixels (always 16).
        rows (List[int]): The bitmap data.
    """

    width: int
    height: int
    rows: List[int]

    def display(self) -> str:
        return "\n".join(
            f"( {row:0{self.width}b} )".translate({48: "・", 49: "██"})
            for row in self.rows
        )

    def uxn_bytes(self) -> bytes:
        return bytes(
            [
                row >> k & 255
                for seg in (self.rows[:8], self.rows[8:])
                for k in range(self.width - 8, -1, -8)
                for row in seg
            ]
        )


def read_font(file_name: str) -> Dict[str, Glyph]:
    font: Dict[str, Glyph] = {}
    character: str = ""
    width: int = 0
    rows: List[int] = []
    reading_bitmap: bool = False
    for line in open(file_name, encoding="ascii"):
        if line.startswith("CHARSET_REGISTRY"):
            assert "JIS" in line.upper()
        elif line.startswith("ENCODING"):
            jis_code = int(line.split()[1])
            if jis_code == 0xA0:
                character = "invalid"
            elif jis_code < 256:
                try:
                    character = bytes([jis_code]).decode("shift_jis")
                except UnicodeDecodeError:
                    character = "invalid"
            else:
                jis_bytes = jis_code.to_bytes(2, byteorder="big")
                try:
                    character = (b"\033$B" + jis_bytes).decode("iso2022_jp")
                except UnicodeDecodeError:
                    character = "invalid"
        elif line.startswith("DWIDTH"):
            width = int(line.split()[1])
        elif line.startswith("BITMAP"):
            reading_bitmap = True
        elif line.startswith("ENDCHAR"):
            assert character and width
            assert character not in font
            if character != "invalid":
                font[character] = Glyph(width, 16, rows)
            character = ""
            width = 0
            rows = []
            reading_bitmap = False
        elif reading_bitmap:
            rows.append(int(line, 16))
    return font


def prehash(character: str) -> int:
    """We don't need to really decode UTF-8 in uxn. We do this instead:"""
    s = 0
    for b in character.encode("utf-8"):
        s = (s << 6) + b
    return s & 0xFFFF


if not sys.argv[2:]:
    sys.exit("usage: make.py app.tal [bdf fonts]")

font = {}
for font_name in sys.argv[2:]:
    font.update(read_font(font_name))

# There are no prehash collisions:
assert len({prehash(c) for c in font}) == len(font)


# We can use two range checks to predict glyph width:
assert all(
    (0x1FE0 < prehash(c) < 0x2020 or prehash(c) < 0x80) == (glyph.width == 8)
    for c, glyph in font.items()
)


def find_mod_chain(
    numbers: List[int], second_mod_is_power_of_2: bool = False, coarseness: int = 7
) -> List[int]:
    """
    Find integers [A, B] so that `numbers[i] % A % B` are all distinct, and B is
    as small as possible.

    Arguments:
        numbers: The domain to hash from.
        second_mod_is_power_of_2: Limit B to powers of 2.
        coarseness: Increment to use when trying values for A.
    """
    n = len(numbers)
    M = max(numbers)
    for mB in range(n, M):
        if second_mod_is_power_of_2 and (mB & mB - 1) != 0:
            continue
        for mA in range(mB, M, coarseness):
            d2 = set()
            ok2 = True
            for x in numbers:
                if (z := x % mA % mB) in d2:
                    ok2 = False
                    break
                d2.add(z)
            if not ok2:
                continue
            return [mA, mB]
    raise Exception("no mod chain found")


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as code_file:
        tokens = code_file.read().split()
    text = "".join(t[1:] for t in tokens if t.startswith('"')) + " 　"
    alphabet = sorted({prehash(c) for c in text})
    modulos = find_mod_chain(alphabet)

    uxn_lut = bytearray()
    uxn_font_data = bytearray()
    i = 0
    for c in sorted(set(text)):
        glyph = font[c]
        h = prehash(c)
        for m in modulos:
            h %= m
        h *= 2
        uxn_lut = uxn_lut.ljust(h + 2, b"\0")
        uxn_lut[h : h + 2] = i.to_bytes(2, byteorder="big")
        bs = glyph.uxn_bytes()
        uxn_font_data += bs
        i += len(bs) // 16

    with open("font.tal", "w", encoding="ascii") as font_tal:
        print(f"@font-mod1 {modulos[0]:04x}", file=font_tal)
        print(f"@font-mod2 {modulos[1]:04x}", file=font_tal)
        print("@font-lut", file=font_tal)
        for i in range(0, len(uxn_lut), 32):
            print("    " + uxn_lut[i : i + 32].hex(" ", 2), file=font_tal)
        print("@font", file=font_tal)
        for i in range(0, len(uxn_font_data), 32):
            print("    " + uxn_font_data[i : i + 32].hex(" ", 2), file=font_tal)

    print(
        f"Wrote {4 + len(uxn_lut) + len(uxn_font_data)} bytes of font data to font.tal"
    )
