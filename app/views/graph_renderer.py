from __future__ import annotations

import io
import urllib.request
from functools import lru_cache

from gi.repository import GdkPixbuf

from app.config import REQUEST_TIMEOUT

try:
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib.figure import Figure
    import numpy as np

    _MATPLOTLIB_AVAILABLE = True
except Exception:  # noqa: BLE001
    _MATPLOTLIB_AVAILABLE = False


class GraphRenderError(Exception):
    """Raised when graph media cannot be rendered into a pixbuf."""


def render_graph_pixbuf_from_url(
    image_url: str,
    max_width: int = 520,
    max_height: int = 280,
) -> GdkPixbuf.Pixbuf:
    """Render a Wolfram graph image URL through matplotlib and return a GTK pixbuf."""
    normalized_url = (image_url or "").strip()
    if not normalized_url:
        raise GraphRenderError("Missing graph image URL.")

    png_bytes = _render_graph_png_bytes(normalized_url, max_width, max_height)
    if png_bytes is None:
        raise GraphRenderError("Failed to render graph image.")

    return _pixbuf_from_png_bytes(png_bytes)


def _pixbuf_from_png_bytes(png_bytes: bytes) -> GdkPixbuf.Pixbuf:
    loader = GdkPixbuf.PixbufLoader.new_with_type("png")
    loader.write(png_bytes)
    loader.close()
    pixbuf = loader.get_pixbuf()
    if pixbuf is None:
        raise GraphRenderError("Failed to decode graph image.")
    return pixbuf


@lru_cache(maxsize=128)
def _render_graph_png_bytes(image_url: str, max_width: int, max_height: int) -> bytes | None:
    if not _MATPLOTLIB_AVAILABLE:
        return None

    try:
        request = urllib.request.Request(
            image_url,
            headers={"User-Agent": "MathSolver/1.0"},
        )
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            raw_image = response.read()

        image_data = _decode_image_bytes_to_array(raw_image)
        source_height, source_width = image_data.shape[:2]

        scale = min(max_width / source_width, max_height / source_height, 1.0)
        dpi = 120
        figure_width = max(1.0, (source_width * scale) / dpi)
        figure_height = max(0.8, (source_height * scale) / dpi)

        figure = Figure(figsize=(figure_width, figure_height), dpi=dpi)
        axis = figure.add_subplot(111)
        axis.axis("off")
        axis.set_position([0, 0, 1, 1])
        axis.imshow(image_data)

        buffer = io.BytesIO()
        figure.savefig(
            buffer,
            format="png",
            bbox_inches="tight",
            pad_inches=0.0,
            transparent=True,
        )
        return buffer.getvalue()
    except Exception:  # noqa: BLE001
        return None


def _decode_image_bytes_to_array(raw_image: bytes) -> np.ndarray:
    loader = GdkPixbuf.PixbufLoader.new()
    loader.write(raw_image)
    loader.close()
    pixbuf = loader.get_pixbuf()
    if pixbuf is None:
        raise GraphRenderError("Unable to decode Wolfram image.")

    width = pixbuf.get_width()
    height = pixbuf.get_height()
    channels = pixbuf.get_n_channels()
    rowstride = pixbuf.get_rowstride()

    if channels not in (3, 4):
        raise GraphRenderError("Unsupported image channel count.")

    pixel_bytes = bytes(pixbuf.get_pixels())
    row_data = np.frombuffer(pixel_bytes, dtype=np.uint8).reshape((height, rowstride))
    packed = row_data[:, : width * channels]
    return packed.reshape((height, width, channels))
