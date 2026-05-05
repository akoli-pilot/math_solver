from __future__ import annotations

from gi.repository import Gtk

from app.models.wolfram_model import MathElement
from app.views.graph_renderer import GraphRenderError, render_graph_pixbuf_from_url
from app.views.latex_renderer import LatexRenderError, render_latex_pixbuf
from app.models.dictionary import DICTIONARY


def is_graph_like_element(element: MathElement) -> bool:
    graph_keywords = (
        "plot",
        "graph",
        "curve",
        "function",
        "parametric",
        "implicit",
        "contour",
        "surface",
    )
    searchable = f"{element.pod_id} {element.pod_title} {element.title}".lower()
    return any(keyword in searchable for keyword in graph_keywords)


def render_latex_fallback(image_widget: Gtk.Image, content: str, font_size: int = 18) -> None:
    try:
        equation_pixbuf = render_latex_pixbuf(content, font_size=font_size)
        image_widget.set_from_pixbuf(equation_pixbuf)
    except LatexRenderError:
        image_widget.clear()


def apply_math_element_image(
    image_widget: Gtk.Image,
    element: MathElement,
    font_size: int = 18,
    max_width: int = 520,
    max_height: int = 280,
) -> None:
    display_text = (element.display_text or element.title or "").strip()

    if element.image_source:
        try:
            graph_pixbuf = render_graph_pixbuf_from_url(
                element.image_source,
                max_width=max_width,
                max_height=max_height,
            )
            image_widget.set_from_pixbuf(graph_pixbuf)
            return
        except GraphRenderError:
            pass

    if display_text:
        render_latex_fallback(image_widget, display_text, font_size=font_size)
    else:
        image_widget.clear()

# Scans the text for matching terms from the dictionary
def _detect_terms(text: str) -> list[str]:
    text_lower = text.lower()
    matched = []
    for entry in DICTIONARY:
        term = entry["term"]
        if term.lower() in text_lower:
            matched.append(term)
    return matched

class MathElementCard(Gtk.Button):
    def __init__(self, element: MathElement, on_click: callable) -> None:
        super().__init__()
        self.element = element
        self.set_relief(Gtk.ReliefStyle.NONE)
        self.set_hexpand(True)
        self.set_halign(Gtk.Align.FILL)
        self.get_style_context().add_class("math-card")
        self.connect("clicked", self._handle_click, on_click)
        body_text = element.display_text.strip() or element.title.strip()
        self._matched_terms = _detect_terms(element.pod_title + " " + body_text)
        self._popup_term = self._matched_terms[0] if self._matched_terms else element.pod_title

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

        kicker_label = Gtk.Label(label=element.pod_title)
        kicker_label.set_xalign(0)
        kicker_label.get_style_context().add_class("card-kicker")

        title_label = Gtk.Label(label=element.title or "")
        title_label.set_xalign(0)
        title_label.set_line_wrap(True)
        title_label.set_max_width_chars(55)
        title_label.get_style_context().add_class("card-title")

        if not element.title.strip() or element.title in {"Result", "Math Result"}:
            title_label.set_no_show_all(True)
            title_label.hide()

        equation_image = Gtk.Image()
        apply_math_element_image(equation_image, element)

        equation_image.set_halign(Gtk.Align.START)
        equation_image.get_style_context().add_class("equation-image")

        content_box.pack_start(kicker_label, False, False, 0)
        content_box.pack_start(title_label, False, False, 0)
        content_box.pack_start(equation_image, False, False, 0)

        self.add(content_box)

        if self._matched_terms:
            chips_box = Gtk.FlowBox()
            chips_box.set_selection_mode(Gtk.SelectionMode.NONE)
            chips_box.set_max_children_per_line(6)
            chips_box.set_column_spacing(6)
            chips_box.set_row_spacing(4)
            chips_box.set_margin_top(6)
            for term in self._matched_terms:
                chip = Gtk.Button(label=term)
                chip.get_style_context().add_class("tag-chip")
                chip.get_style_context().add_class("term-chip")
                chips_box.add(chip)
            content_box.pack_start(chips_box, False, False, 0)

    def _handle_click(self, _button: Gtk.Button, on_click: callable) -> None:
        on_click(self.element, self._popup_term)
