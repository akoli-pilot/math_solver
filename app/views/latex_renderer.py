from __future__ import annotations

import io
from functools import lru_cache

from gi.repository import GdkPixbuf

try:
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib.figure import Figure

    _MATPLOTLIB_AVAILABLE = True
except Exception:  # noqa: BLE001
    _MATPLOTLIB_AVAILABLE = False


class LatexRenderError(Exception):
    """Raised when LaTeX cannot be rendered into a pixbuf."""


def render_latex_pixbuf(expression: str, font_size: int = 18) -> GdkPixbuf.Pixbuf:
    """Render a LaTeX equation to a transparent pixbuf for GTK widgets."""
    if not _MATPLOTLIB_AVAILABLE:
        raise LatexRenderError("Matplotlib is required for LaTeX rendering.")

    prepared = _prepare_expression(expression)
    candidates = _candidate_equations(prepared)

    for candidate in candidates:
        png_bytes = _render_latex_png_bytes(candidate, font_size)
        if png_bytes is not None:
            return _pixbuf_from_png_bytes(png_bytes)

    for fallback in ("x", "1", r"\sqrt{2}"):
        error_png = _render_latex_png_bytes(fallback, font_size)
        if error_png is not None:
            return _pixbuf_from_png_bytes(error_png)

    raise LatexRenderError("Unable to render equation.")


def _pixbuf_from_png_bytes(png_bytes: bytes) -> GdkPixbuf.Pixbuf:
    loader = GdkPixbuf.PixbufLoader.new_with_type("png")
    loader.write(png_bytes)
    loader.close()
    pixbuf = loader.get_pixbuf()
    if pixbuf is None:
        raise LatexRenderError("Failed to create pixbuf from rendered equation.")
    return pixbuf


@lru_cache(maxsize=256)
def _render_latex_png_bytes(equation_body: str, font_size: int) -> bytes | None:
    equation = _as_mathtext(equation_body)

    figure = Figure(figsize=(6.4, 1.3), dpi=180)
    axis = figure.add_subplot(111)
    axis.axis("off")

    try:
        axis.text(
            0.01,
            0.5,
            equation,
            fontsize=font_size,
            color="#e2e7e3",
            va="center",
            ha="left",
        )

        buffer = io.BytesIO()
        figure.savefig(
            buffer,
            format="png",
            bbox_inches="tight",
            pad_inches=0.05,
            transparent=True,
        )
        return buffer.getvalue()
    except Exception:  # noqa: BLE001
        return None


def _as_mathtext(prepared_expression: str) -> str:
    if prepared_expression.startswith("$") and prepared_expression.endswith("$"):
        return prepared_expression
    return f"${prepared_expression}$"


def _prepare_expression(expression: str) -> str:
    if not expression:
        return r"\varnothing"

    first_line = ""
    for line in expression.splitlines():
        trimmed = line.strip()
        if trimmed:
            first_line = trimmed
            break

    if not first_line:
        return r"\varnothing"

    normalized = first_line
    normalized = normalized.replace("−", "-")
    normalized = normalized.replace("×", r"\times ")
    normalized = normalized.replace("÷", r"\div ")
    normalized = normalized.replace("π", r"\pi")
    normalized = normalized.replace("∞", r"\infty")

    if len(normalized) > 260:
        normalized = normalized[:260]

    return normalized


def _candidate_equations(prepared: str) -> list[str]:
    equations: list[str] = []

    if prepared.startswith("$") and prepared.endswith("$"):
        equations.append(prepared)
    else:
        equations.append(prepared)
        equations.append(rf"\mathrm{{{_escape_latex_text(prepared)}}}")

    return equations


def _escape_latex_text(value: str) -> str:
    escaped = value
    escaped = escaped.replace("\\", r"\backslash ")
    escaped = escaped.replace("{", r"\{")
    escaped = escaped.replace("}", r"\}")
    escaped = escaped.replace("#", r"\#")
    escaped = escaped.replace("$", r"\$")
    escaped = escaped.replace("%", r"\%")
    escaped = escaped.replace("&", r"\&")
    escaped = escaped.replace("_", r"\_")
    escaped = escaped.replace("^", r"\^{}")
    escaped = escaped.replace("~", r"\sim ")
    escaped = escaped.replace(" ", r"\ ")
    return escaped
