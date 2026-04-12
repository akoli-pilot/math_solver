from __future__ import annotations

import os

from gi.repository import Gdk, Gtk

_THEME_LOADED = False


def load_material_theme() -> None:
    global _THEME_LOADED
    if _THEME_LOADED:
        return

    settings = Gtk.Settings.get_default()
    if settings is not None:
        settings.set_property("gtk-application-prefer-dark-theme", True)

    css_path = os.path.join(os.path.dirname(__file__), "material_theme.css")
    css_provider = Gtk.CssProvider()
    css_provider.load_from_path(css_path)

    screen = Gdk.Screen.get_default()
    if screen is None:
        return

    Gtk.StyleContext.add_provider_for_screen(
        screen,
        css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )
    _THEME_LOADED = True
