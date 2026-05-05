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

        self._new_tab_handler = None

        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.set_tab_pos(Gtk.PositionType.TOP)
        self.add(self.notebook)

        self.workspace = self.add_solver_tab()

        self.add_tab_button = Gtk.Button(label="+")
        self.add_tab_button.set_tooltip_text("New Tab")
        self.add_tab_button.set_relief(Gtk.ReliefStyle.NONE)
        self.add_tab_button.connect("clicked", self._on_add_tab_clicked)
        self.notebook.set_action_widget(self.add_tab_button, Gtk.PackType.END)
        self.add_tab_button.show()

    def add_solver_tab(self) -> SolverWorkspace:
        workspace = SolverWorkspace()

        tab_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        tab_label = Gtk.Label(label="Tab")

        close_button = Gtk.Button(label="x")
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        close_button.set_focus_on_click(False)
        close_button.connect("clicked", self._on_close_tab_clicked, workspace)

        tab_box.pack_start(tab_label, True, True, 0)
        tab_box.pack_start(close_button, False, False, 0)
        tab_box.show_all()

        self.notebook.append_page(workspace, tab_box)
        self.notebook.set_tab_reorderable(workspace, True)
        self.notebook.set_current_page(-1)

        self._renumber_tabs()
        workspace.show_all()
        return workspace

    def set_new_tab_handler(self, handler) -> None:
        self._new_tab_handler = handler

    def _on_add_tab_clicked(self, _button: Gtk.Button) -> None:
        if self._new_tab_handler is not None:
            self._new_tab_handler()

    def _on_close_tab_clicked(self, _button: Gtk.Button, workspace: SolverWorkspace) -> None:
        page_num = self.notebook.page_num(workspace)

        if page_num == -1:
            return

        if self.notebook.get_n_pages() <= 1:
            return

        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Are you sure you want to close that tab?",
        )
        dialog.format_secondary_text("This action cannot be undone")

        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            self.notebook.remove_page(page_num)
            self._renumber_tabs()

    def _renumber_tabs(self) -> None:
        for index in range(self.notebook.get_n_pages()):
            page = self.notebook.get_nth_page(index)
            tab_widget = self.notebook.get_tab_label(page)

            if isinstance(tab_widget, Gtk.Box):
                children = tab_widget.get_children()
                if children:
                    label = children[0]
                    if isinstance(label, Gtk.Label):
                        label.set_text(f"Tab {index + 1}")