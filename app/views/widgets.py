from __future__ import annotations

from gi.repository import Gtk

from app.models.wolfram_model import MathElement
from app.views.graph_renderer import GraphRenderError, render_graph_pixbuf_from_url
from app.views.latex_renderer import LatexRenderError, render_latex_pixbuf


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

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

        kicker_label = Gtk.Label(label=element.pod_title)
        kicker_label.set_xalign(0)
        kicker_label.get_style_context().add_class("card-kicker")

        title_label = Gtk.Label(label=element.title or "Math Result")
        title_label.set_xalign(0)
        title_label.set_line_wrap(True)
        title_label.set_max_width_chars(55)
        title_label.get_style_context().add_class("card-title")

        equation_image = Gtk.Image()
        should_render_graph = bool(element.image_source) and self._is_graph_like_element(element)

        if should_render_graph:
            try:
                graph_pixbuf = render_graph_pixbuf_from_url(element.image_source)
                equation_image.set_from_pixbuf(graph_pixbuf)
            except GraphRenderError:
                self._render_latex_fallback(equation_image, body_text)
        else:
            self._render_latex_fallback(equation_image, body_text)

        equation_image.set_halign(Gtk.Align.START)
        equation_image.get_style_context().add_class("equation-image")

        content_box.pack_start(kicker_label, False, False, 0)
        content_box.pack_start(title_label, False, False, 0)
        content_box.pack_start(equation_image, False, False, 0)

        self.add(content_box)

    @staticmethod
    def _is_graph_like_element(element: MathElement) -> bool:
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

    @staticmethod
    def _render_latex_fallback(image_widget: Gtk.Image, content: str) -> None:
        try:
            equation_pixbuf = render_latex_pixbuf(content, font_size=18)
            image_widget.set_from_pixbuf(equation_pixbuf)
        except LatexRenderError:
            image_widget.clear()

    def _handle_click(self, _button: Gtk.Button, on_click: callable) -> None:
        on_click(self.element)
