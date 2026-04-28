from __future__ import annotations

from gi.repository import GLib, Gtk, Gdk

from app.views.equation_editor import EquationEditor
from app.views.theme import load_material_theme


class MainView(Gtk.Window):
    def __init__(self, title: str) -> None:
        super().__init__(title=title)
        load_material_theme()
        self._progress_timeout_id: int | None = None

        self.set_default_size(1120, 760)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("destroy", Gtk.main_quit)
        self.get_style_context().add_class("main-window")

        page_scroller = Gtk.ScrolledWindow()
        page_scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        page_scroller.set_shadow_type(Gtk.ShadowType.NONE)
        page_scroller.set_hexpand(True)
        page_scroller.set_vexpand(True)
        self.add(page_scroller)

        root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        root_box.get_style_context().add_class("top-shell")
        page_scroller.add(root_box)

        top_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        top_panel.get_style_context().add_class("surface-panel")

        headline = Gtk.Label(label="Interactive Math Solver")
        headline.set_xalign(0)
        headline.get_style_context().add_class("headline")

        subtitle = Gtk.Label(
            label="Powered by Wolfram Alpha")
        subtitle.set_xalign(0)
        subtitle.set_line_wrap(True)
        subtitle.get_style_context().add_class("subtitle")

        query_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.query_editor = EquationEditor(
            placeholder="Build your equation with numbers, operators, and special constants, then press Solve.",
        )
        self.query_editor.set_hexpand(True)

        self.solve_button = Gtk.Button(label="Solve")
        self.solve_button.get_style_context().add_class("filled-button")

        query_row.pack_start(self.query_editor, True, True, 0)
        query_row.pack_start(self.solve_button, False, False, 0)

        status_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.spinner = Gtk.Spinner()
        self.status_label = Gtk.Label(label="Ready")
        self.status_label.set_xalign(0)
        self.status_label.set_hexpand(True)
        self.status_label.get_style_context().add_class("status-chip")
        self.status_label.get_style_context().add_class("status-info")

        status_row.pack_start(self.spinner, False, False, 0)
        status_row.pack_start(self.status_label, True, True, 0)

        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(False)
        self.progress_bar.set_hexpand(True)
        self.progress_bar.set_no_show_all(True)
        self.progress_bar.get_style_context().add_class("material-progress")

        top_panel.pack_start(headline, False, False, 0)
        top_panel.pack_start(subtitle, False, False, 0)
        top_panel.pack_start(query_row, False, False, 0)
        top_panel.pack_start(status_row, False, False, 0)
        top_panel.pack_start(self.progress_bar, False, False, 0)

        results_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        results_panel.get_style_context().add_class("surface-panel")

        section_title = Gtk.Label(label="Math Elements")
        section_title.set_xalign(0)
        section_title.get_style_context().add_class("section-title")

        self.results_flow = Gtk.FlowBox()
        self.results_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.results_flow.set_max_children_per_line(2)
        self.results_flow.set_min_children_per_line(1)
        self.results_flow.set_column_spacing(14)
        self.results_flow.set_row_spacing(14)
        self.results_flow.set_activate_on_single_click(True)
        self.results_flow.set_hexpand(True)

        results_panel.pack_start(section_title, False, False, 0)
        results_panel.pack_start(self.results_flow, False, True, 0)

        root_box.pack_start(top_panel, False, False, 0)
        root_box.pack_start(results_panel, False, False, 0)

    def connect_signals(self, controller: object) -> None:
        self.solve_button.connect("clicked", controller.on_solve_requested)
        self.query_editor.connect_submit(lambda: controller.on_solve_requested())
        
        # ADD KEYBOARD SUPPORT 
        self.connect("key-press-event", lambda w, e: self._on_key_press(e, controller))
        self.set_can_focus(True)

    def get_query(self) -> str:
        return self.query_editor.get_latex()

    def set_status(self, message: str, tone: str = "info") -> None:
        context = self.status_label.get_style_context()
        context.remove_class("status-info")
        context.remove_class("status-success")
        context.remove_class("status-error")

        self.status_label.set_text(message)

        if tone == "error":
            context.add_class("status-error")
        elif tone == "success":
            context.add_class("status-success")
        else:
            context.add_class("status-info")

    def set_loading(self, is_loading: bool) -> None:
        if is_loading:
            self.spinner.start()
            self.progress_bar.show()
            if self._progress_timeout_id is None:
                self._progress_timeout_id = GLib.timeout_add(120, self._pulse_progress)
        else:
            self.spinner.stop()
            if self._progress_timeout_id is not None:
                GLib.source_remove(self._progress_timeout_id)
                self._progress_timeout_id = None
            self.progress_bar.hide()

        self.solve_button.set_sensitive(not is_loading)

    def _pulse_progress(self) -> bool:
        self.progress_bar.pulse()
        return True

    def clear_results(self) -> None:
        for child in self.results_flow.get_children():
            self.results_flow.remove(child)

    def add_math_element_widget(self, widget: Gtk.Widget) -> None:
        self.results_flow.add(widget)
    
    #keyboard support feature    
    def _on_key_press(self, event, controller):
        from gi.repository import Gdk

        key = event.keyval

        # Enter → Solve
        if key == Gdk.KEY_Return:
            controller.on_solve_requested()
            return True

        return False
