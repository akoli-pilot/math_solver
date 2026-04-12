from __future__ import annotations

from abc import ABC, abstractmethod

from gi.repository import Gtk

from app.models.wolfram_model import MathElement
from app.views.widgets import MathElementCard


class UIComponentFactory(ABC):
    @abstractmethod
    def create_math_element_widget(self, element: MathElement, on_click: callable) -> Gtk.Widget:
        raise NotImplementedError


class MaterialWindowFactory(UIComponentFactory):
    def create_math_element_widget(self, element: MathElement, on_click: callable) -> Gtk.Widget:
        return MathElementCard(element=element, on_click=on_click)
