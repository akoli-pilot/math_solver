from __future__ import annotations

from gi.repository import Gtk

from app.models.wolfram_model import MathElement
from app.views.theme import load_material_theme
from app.views.widgets import apply_math_element_image


class MathElementWindow(Gtk.Window):
    def __init__(self, element: MathElement, parent: Gtk.Window | None = None) -> None:
        title_text = (element.title or element.pod_title or "Math Element").strip() or "Math Element"
        super().__init__(title=title_text)
        load_material_theme()

        self.set_default_size(760, 520)
        self.get_style_context().add_class("explanation-window")

        if parent is not None:
            self.set_transient_for(parent)
            self.set_destroy_with_parent(True)

        root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root_box.get_style_context().add_class("top-shell")
        self.add(root_box)

        content_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content_panel.get_style_context().add_class("surface-panel")
        root_box.pack_start(content_panel, True, True, 0)

        kicker_label = Gtk.Label(label=element.pod_title or "Result")
        kicker_label.set_xalign(0)
        kicker_label.get_style_context().add_class("card-kicker")

        title_label = Gtk.Label(label=element.title or "Math Result")
        title_label.set_xalign(0)
        title_label.set_line_wrap(True)
        title_label.get_style_context().add_class("card-title")

        equation_image = Gtk.Image()
        equation_image.set_halign(Gtk.Align.START)
        equation_image.get_style_context().add_class("equation-image")
        apply_math_element_image(
            equation_image,
            element,
            font_size=22,
            max_width=820,
            max_height=460,
        )

        content_panel.pack_start(kicker_label, False, False, 0)
        content_panel.pack_start(title_label, False, False, 0)
        content_panel.pack_start(equation_image, False, False, 0)

        body_text = (element.display_text or "").strip()
        if body_text and body_text != (element.title or "").strip():
            body_label = Gtk.Label(label=body_text)
            body_label.set_xalign(0)
            body_label.set_line_wrap(True)
            body_label.get_style_context().add_class("card-body")
            content_panel.pack_start(body_label, False, False, 0)
