from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from gi.repository import GLib

from app.factories.window_factory import UIComponentFactory
from app.models.wolfram_model import MathElement, SolverResult, WolframSolverModel
from app.views.main_view import MainView

if TYPE_CHECKING:
    from gi.repository import Gtk


class SolverController:
    def __init__(
        self,
        model: WolframSolverModel,
        main_view: SolverWorkspace,
        component_factory: UIComponentFactory,
    ) -> None:
        self.model = model
        self.main_view = main_view
        self.component_factory = component_factory
        self._detail_windows: list[Gtk.Window] = []

        self._history: list[str] = []
        self._history_index: int | None = None

    def on_solve_requested(self, *_args: object) -> None:
        query = self.main_view.get_query()
        if not query:
            self.main_view.set_status("Enter a math query first.", tone="error")
            return

        self.main_view.clear_results()
        self.main_view.set_loading(True)
        self.main_view.set_status("Consulting Wolfram...", tone="info")
        self._run_background(
            task=lambda: self.model.solve(query),
            callback=self._on_main_result,
        )

    def _remember_query(self, query: str) -> None:
        normalized = (query or "").strip()
        if not normalized:
            return

        if not self._history or self._history[-1] != normalized:
            self._history.append(normalized)

        self._history_index = None

    def on_history_previous(self) -> None:
        if not self._history:
            return

        if self._history_index is None:
            self._history_index = len(self._history) - 1
        elif self._history_index > 0:
            self._history_index -= 1

        self.main_view.query_editor.set_latex(self._history[self._history_index])
        self.main_view.set_status(
            f"History {self._history_index + 1}/{len(self._history)}",
            tone="info",
        )

    def on_history_next(self) -> None:
        if not self._history or self._history_index is None:
            return

        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self.main_view.query_editor.set_latex(self._history[self._history_index])
            self.main_view.set_status(
                f"History {self._history_index + 1}/{len(self._history)}",
                tone="info",
            )
        else:
            self._history_index = None
            self.main_view.query_editor.set_latex("")
            self.main_view.set_status("Ready", tone="info")

    # Pops up the card when the result element is clicked
    def _on_math_element_selected(self, element: object, term: str = None) -> None:
        from app.views.dictionary_card import show_dictionary_popup
        
        for flow_child in self.main_view.results_flow.get_children():
            card = flow_child.get_child()
            if hasattr(card, "element") and card.element is element:
                popup_term = term or card.element.pod_title
                show_dictionary_popup(card, popup_term)
                return

    def _run_background(self, task: callable, callback: callable) -> None:
        def worker() -> None:
            result = task()
            GLib.idle_add(callback, result)

        threading.Thread(target=worker, daemon=True).start()

    def _on_main_result(self, result: SolverResult) -> bool:
        self.main_view.set_loading(False)

        if result.elements:
            self._remember_query(result.query)
            
            for element in result.elements:
                card = self.component_factory.create_math_element_widget(
                    element=element,
                    on_click=self._on_math_element_selected,
                )
                self.main_view.add_math_element_widget(card)

            status_parts = [f"Loaded {len(result.elements)} elements"]
            if result.assumptions:
                status_parts.append(f"assumptions: {result.assumptions[0]}")
            self.main_view.set_status(" | ".join(status_parts), tone="success")
        else:
            if result.messages:
                self.main_view.set_status(result.messages[0], tone="error")
            else:
                self.main_view.set_status("No interactive math elements were returned.", tone="error")

        self.main_view.show_all()
        return False
