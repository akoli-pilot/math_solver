from __future__ import annotations

from abc import ABC, abstractmethod

from gi.repository import Gtk

from app.models.wolfram_model import MathElement
from app.views.math_element_window import MathElementWindow
from app.views.widgets import MathElementCard


class UIComponentFactory(ABC):
    @abstractmethod
    def create_math_element_widget(self, element: MathElement, on_click: callable) -> Gtk.Widget:
        raise NotImplementedError

    @abstractmethod
    def create_math_element_window(
        self,
        element: MathElement,
        parent: Gtk.Window | None = None,
    ) -> Gtk.Window:
        raise NotImplementedError


class MaterialWindowFactory(UIComponentFactory):
    def create_math_element_widget(self, element: MathElement, on_click: callable) -> Gtk.Widget:
        return MathElementCard(element=element, on_click=on_click)

    def create_math_element_window(
        self,
        element: MathElement,
        parent: Gtk.Window | None = None,
    ) -> Gtk.Window:
        return MathElementWindow(element=element, parent=parent)
