"""Создаёт static/img/logo.png (белый мяч на синем квадрате) без сторонних библиотек."""

import struct
import zlib
from pathlib import Path

SIZE = 64
BACKGROUND = (30, 86, 160)
FOREGROUND = (255, 255, 255)
OUTER_RADIUS = 26
INNER_RADIUS = 22
BAR_HALF_HEIGHT = 2

OUTPUT_PATH = Path(__file__).resolve().parent.parent / 'static' / 'img' / 'logo.png'


def make_chunk(tag, data):
    body = tag + data
    checksum = zlib.crc32(body) & 0xFFFFFFFF
    return struct.pack('>I', len(data)) + body + struct.pack('>I', checksum)


def build_raw_image():
    center = (SIZE - 1) / 2
    rows = bytearray()
    for y in range(SIZE):
        rows.append(0)  # тип фильтра строки: без фильтрации
        for x in range(SIZE):
            distance_squared = (x - center) ** 2 + (y - center) ** 2
            on_ring = INNER_RADIUS ** 2 <= distance_squared <= OUTER_RADIUS ** 2
            on_bar = (
                abs(y - center) <= BAR_HALF_HEIGHT
                and distance_squared <= OUTER_RADIUS ** 2
            )
            color = FOREGROUND if (on_ring or on_bar) else BACKGROUND
            rows.extend(color)
    return bytes(rows)


def write_logo():
    header = struct.pack('>IIBBBBB', SIZE, SIZE, 8, 2, 0, 0, 0)
    png = (
        b'\x89PNG\r\n\x1a\n'
        + make_chunk(b'IHDR', header)
        + make_chunk(b'IDAT', zlib.compress(build_raw_image(), 9))
        + make_chunk(b'IEND', b'')
    )
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_bytes(png)
    print(f'Логотип сохранён: {OUTPUT_PATH}')


if __name__ == '__main__':
    write_logo()