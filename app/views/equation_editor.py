from __future__ import annotations

from gi.repository import Gtk, GLib

from app.views.latex_renderer import LatexRenderError, render_latex_pixbuf


class EquationEditor(Gtk.Box):
    def __init__(self, placeholder: str) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_hexpand(True)
        self.get_style_context().add_class("equation-editor")

        self._submit_callback: callable | None = None
        self._latex_text = ""

        hint_label = Gtk.Label(label=placeholder)
        hint_label.set_xalign(0)
        hint_label.get_style_context().add_class("editor-hint")
        
        self.text_entry = Gtk.Entry()
        self.text_entry.grab_focus()
        self.text_entry.set_placeholder_text("Type your equation...")
        self.text_entry.set_hexpand(True)

        # when typing → update latex
        self.text_entry.connect("changed", self._on_text_changed)

        # Press Enter → submit
        self.text_entry.connect("activate", self._on_entry_submit)

        self.preview_title = Gtk.Label(label="LaTeX Preview")
        self.preview_title.set_xalign(0)
        self.preview_title.get_style_context().add_class("editor-preview-title")

        self.preview_image = Gtk.Image()
        self.preview_image.set_halign(Gtk.Align.START)
        self.preview_image.get_style_context().add_class("equation-image")

        display_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        display_box.get_style_context().add_class("equation-display-shell")
        display_box.pack_start(self.preview_title, False, False, 0)
        display_box.pack_start(self.preview_image, False, False, 0)

        display_frame = Gtk.Frame()
        display_frame.get_style_context().add_class("equation-display-frame")
        display_frame.add(display_box)

        self.preview_revealer = Gtk.Revealer()
        self.preview_revealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
        self.preview_revealer.set_reveal_child(False)
        self.preview_revealer.add(display_frame)

        keypad_grid = Gtk.Grid()
        keypad_grid.set_row_spacing(8)
        keypad_grid.set_column_spacing(8)
        keypad_grid.get_style_context().add_class("keypad-grid")

        self._build_keypad(keypad_grid)

        self.pack_start(hint_label, False, False, 0)
        self.pack_start(self.text_entry, False, False, 0)
        self.pack_start(self.preview_revealer, False, False, 0)
        self.pack_start(keypad_grid, False, False, 0)

        self._refresh_preview()

    def connect_submit(self, callback: callable) -> None:
        self._submit_callback = callback

    def get_latex(self) -> str:
        return self._latex_text.strip()

    def set_latex(self, value: str) -> None:
        self._latex_text = (value or "").strip()
        self.text_entry.set_text(self._latex_text)
        self._refresh_preview()

    def _build_keypad(self, grid: Gtk.Grid) -> None:
        buttons = [
            (0, 0, "1", "append", "1", "number", 1),
            (1, 0, "2", "append", "2", "number", 1),
            (2, 0, "3", "append", "3", "number", 1),
            (3, 0, "+", "append", "+", "operator", 1),
            (4, 0, "DEL", "delete", "", "action", 1),

            (0, 1, "4", "append", "4", "number", 1),
            (1, 1, "5", "append", "5", "number", 1),
            (2, 1, "6", "append", "6", "number", 1),
            (3, 1, "-", "append", "-", "operator", 1),
            (4, 1, "INT", "integral_request", "", "function", 1),

            (0, 2, "7", "append", "7", "number", 1),
            (1, 2, "8", "append", "8", "number", 1),
            (2, 2, "9", "append", "9", "number", 1),
            (3, 2, "*", "append", "*", "operator", 1),
            (4, 2, "d/dx", "derivative_request", "", "function", 1),

            (0, 3, "0", "append", "0", "number", 1),
            (1, 3, ".", "append", ".", "number", 1),
            (2, 3, "=", "append", "=", "operator", 1),
            (3, 3, "/", "append", "/", "operator", 1),
            (4, 3, "^", "append", "^", "operator", 1),

            (0, 4, "pi", "append", r"\pi", "special", 1),
            (1, 4, "e", "append", "e", "special", 1),
            (2, 4, "i", "append", "i", "special", 1),
            (3, 4, "inf", "append", r"\infty", "special", 1),
            (4, 4, "CLR", "clear", "", "action", 1),

            (0, 5, "x", "append", "x", "special", 1),
            (1, 5, "y", "append", "y", "special", 1),
            (2, 5, "(", "append", "(", "special", 1),
            (3, 5, ")", "append", ")", "special", 1),
            (4, 5, "FRAC", "append", "/", "function", 1),
        ]

        for col_index, row_index, label, action, payload, tone, col_span in buttons:
            button = Gtk.Button(label=label)
            button.set_can_focus(False)
            button.set_focus_on_click(False)
            button.set_hexpand(True)
            button.get_style_context().add_class("keypad-button")
            button.get_style_context().add_class(f"keypad-{tone}")
            grid.attach(button, col_index, row_index, col_span, 1)

            if action == "submit":
                button.connect("clicked", self._on_submit)
            else:
                button.connect("clicked", self._handle_keypad_press, action, payload)

    def _get_entry_state(self) -> tuple[str, int, int, int]:
        text = self.text_entry.get_text()

        selection = self.text_entry.get_selection_bounds()
        if selection:
            if len(selection) == 3:
                has_selection, sel_start, sel_end = selection
                if has_selection and sel_start != sel_end:
                    if sel_start > sel_end:
                        sel_start, sel_end = sel_end, sel_start
                    return text, sel_end, sel_start, sel_end
            elif len(selection) == 2:
                sel_start, sel_end = selection
                if sel_start != sel_end:
                    if sel_start > sel_end:
                        sel_start, sel_end = sel_end, sel_start
                    return text, sel_end, sel_start, sel_end

        cursor_pos = len(text)
        return text, cursor_pos, cursor_pos, cursor_pos

    def _set_entry_text(self, new_text: str, cursor_pos: int | None = None) -> None:
        self.text_entry.set_text(new_text)

        if cursor_pos is None:
            cursor_pos = len(new_text)

        cursor_pos = max(0, min(cursor_pos, len(new_text)))
        GLib.idle_add(self._restore_entry_cursor, cursor_pos)

    def _restore_entry_cursor(self, cursor_pos: int) -> bool:
        if hasattr(self.text_entry, "grab_focus_without_selecting"):
            self.text_entry.grab_focus_without_selecting()
        else:
            self.text_entry.grab_focus()

        self.text_entry.set_position(cursor_pos)
        return False

    def _handle_keypad_press(self, _button: Gtk.Button, action: str, payload: str) -> None:
        entry_text, cursor_pos, sel_start, sel_end = self._get_entry_state()

        if action == "append":
            if sel_start != sel_end:
                new_text = entry_text[:sel_start] + payload + entry_text[sel_end:]
                new_cursor = sel_start + len(payload)
            else:
                new_text = entry_text[:cursor_pos] + payload + entry_text[cursor_pos:]
                new_cursor = cursor_pos + len(payload)
            self._set_entry_text(new_text, new_cursor)
            return

        if action == "clear":
            self._set_entry_text("", 0)
            return

        if action == "delete":
            if sel_start != sel_end:
                new_text = entry_text[:sel_start] + entry_text[sel_end:]
                new_cursor = sel_start
            elif cursor_pos > 0:
                new_text = entry_text[: cursor_pos - 1] + entry_text[cursor_pos:]
                new_cursor = cursor_pos - 1
            else:
                return
            self._set_entry_text(new_text, new_cursor)
            return

        if action == "integral_request":
            selection_text = entry_text[sel_start:sel_end] if sel_start != sel_end else entry_text
            expression = selection_text.strip() or "x"
            new_text = f"integral of ({expression})"
            self._set_entry_text(new_text, len(new_text))
            return

        if action == "derivative_request":
            selection_text = entry_text[sel_start:sel_end] if sel_start != sel_end else entry_text
            expression = selection_text.strip() or "x"
            new_text = f"derivative of ({expression})"
            self._set_entry_text(new_text, len(new_text))
            return

        if action == "noop":
            return

    def _on_submit(self, _button: Gtk.Button) -> None:
        if self._submit_callback is not None:
            self._submit_callback()
    
    def _on_text_changed(self, entry):
        self._latex_text = entry.get_text().strip()
        self._refresh_preview()

    def _on_entry_submit(self, entry):
        if self._submit_callback:
            self._submit_callback()

    def _refresh_preview(self) -> None:
        latex_text = self.get_latex()

        if not latex_text:
            self.preview_image.clear()
            self.preview_revealer.set_reveal_child(False)
            return

        try:
            preview_text = self._to_preview_latex(latex_text)
            equation_pixbuf = render_latex_pixbuf(preview_text, font_size=18)
        except LatexRenderError:
            self.preview_image.clear()
            self.preview_revealer.set_reveal_child(False)
            return

        self.preview_image.set_from_pixbuf(equation_pixbuf)
        self.preview_revealer.set_reveal_child(True)

    def _to_preview_latex(self, value: str) -> str:
        expression = (value or "").strip()

        if expression.startswith("integral of (") and expression.endswith(")"):
            inner = expression[len("integral of (") : -1].strip() or "x"
            inner = self._normalize_symbols_for_preview(inner)
            return rf"\int \left({inner}\right)\,dx"

        if expression.startswith("derivative of (") and expression.endswith(")"):
            inner = expression[len("derivative of (") : -1].strip() or "x"
            inner = self._normalize_symbols_for_preview(inner)
            return rf"\frac{{d}}{{dx}}\left({inner}\right)"

        return self._normalize_symbols_for_preview(expression)

    @staticmethod
    def _normalize_symbols_for_preview(expression: str) -> str:
        return expression.replace("*", r"\times ")