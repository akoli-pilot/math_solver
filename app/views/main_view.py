from __future__ import annotations

from gi.repository import Gtk

from app.views.solver_workspace import SolverWorkspace
from app.views.theme import load_material_theme


class MainView(Gtk.Window):
    def __init__(self, title: str) -> None:
        super().__init__(title=title)
        load_material_theme()

        self.set_default_size(1120, 760)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("destroy", Gtk.main_quit)
        self.get_style_context().add_class("main-window")

        self.workspace = SolverWorkspace()
        self.add(self.workspace)