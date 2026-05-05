from __future__ import annotations
import webbrowser
from gi.repository import Gtk
from app.models.dictionary import DICTIONARY

# Looks up an entry from the dictionary
def _find_term(term: str) -> dict | None:
    for entry in DICTIONARY:
        if entry["term"].lower() == term.lower():
            return entry
    return None

# Renders the card on click
class DictionaryPopup(Gtk.Popover):
    def __init__(self, anchor_widget: Gtk.Widget, term_name: str) -> None:
        super().__init__()
        self.set_relative_to(anchor_widget)
        self.set_position(Gtk.PositionType.BOTTOM)
        self.get_style_context().add_class("card-popup")
        self._build(term_name)

    def _build(self, term_name: str) -> None:
        existing = self.get_child()
        if existing:
            self.remove(existing)

        entry = _find_term(term_name)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        outer.set_margin_top(14)
        outer.set_margin_bottom(14)
        outer.set_margin_start(16)
        outer.set_margin_end(16)
        outer.set_size_request(300, -1)

        if not entry:
            label = Gtk.Label(label=f'No entry for "{term_name}".')
            label.get_style_context().add_class("card-summary")
            outer.pack_start(label, False, False, 0)
            self.add(outer)
            self.show_all()
            return

        title = Gtk.Label(label=entry["term"])
        title.set_xalign(0)
        title.set_line_wrap(True)
        title.get_style_context().add_class("card-title")
        outer.pack_start(title, False, False, 0)

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        outer.pack_start(separator, False, False, 0)

        summary = Gtk.Label(label=entry["summary"])
        summary.set_xalign(0)
        summary.set_line_wrap(True)
        summary.set_max_width_chars(45)
        summary.get_style_context().add_class("card-summary")
        outer.pack_start(summary, False, False, 0)

        if entry.get("tags"):
            tags_label = Gtk.Label(label="Related")
            tags_label.set_xalign(0)
            tags_label.get_style_context().add_class("card-kicker")
            outer.pack_start(tags_label, False, False, 0)

            tags_flow = Gtk.FlowBox()
            tags_flow.set_selection_mode(Gtk.SelectionMode.NONE)
            tags_flow.set_max_children_per_line(4)
            tags_flow.set_column_spacing(6)
            tags_flow.set_row_spacing(6)

            for tag in entry["tags"]:
                tag_btn = Gtk.Button(label=tag)
                tag_btn.get_style_context().add_class("tag-chip")
                tag_btn.connect("clicked", self._on_tag_clicked, tag)
                tags_flow.add(tag_btn)

            outer.pack_start(tags_flow, False, False, 0)

        if entry.get("link"):
            link_btn = Gtk.Button(label="Open in MathWorld ↗")
            link_btn.get_style_context().add_class("filled-button")
            link_btn.connect("clicked", self._on_link_clicked, entry["link"])
            outer.pack_start(link_btn, False, False, 0)

        self.add(outer)
        self.show_all()

    # Rebuilds the card with the clicked tag as the new entry
    def _on_tag_clicked(self, _btn: Gtk.Button, term_name: str) -> None:
        self._build(term_name)

    # Opens the link in a web browser
    def _on_link_clicked(self, _btn: Gtk.Button, url: str) -> None:
        webbrowser.open(url)


# Helper function to show popup
def show_dictionary_popup(anchor_widget: Gtk.Widget, term_name: str) -> None:
    popup = DictionaryPopup(anchor_widget, term_name)
    popup.popup()