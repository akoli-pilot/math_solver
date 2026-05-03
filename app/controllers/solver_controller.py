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
        main_view: MainView,
        component_factory: UIComponentFactory,
    ) -> None:
        self.model = model
        self.main_view = main_view
        self.component_factory = component_factory
        self._detail_windows: list[Gtk.Window] = []

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
