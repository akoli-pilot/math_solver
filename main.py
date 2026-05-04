from gi import require_version

require_version("Gtk", "3.0")

from gi.repository import Gtk

from app.config import APP_TITLE, WOLFRAM_APP_ID
from app.controllers.solver_controller import SolverController
from app.factories.window_factory import MaterialWindowFactory
from app.models.wolfram_model import WolframSolverModel
from app.services.wolfram_client import WolframClient
from app.views.main_view import MainView


def build_app() -> MainView:
    client = WolframClient(app_id=WOLFRAM_APP_ID)
    model = WolframSolverModel(client)
    factory = MaterialWindowFactory()
    view = MainView(title=APP_TITLE)

    controller = SolverController(model=model, main_view=view.workspace, component_factory=factory)
    view.workspace.connect_signals(controller)
    return view


if __name__ == "__main__":
    main_window = build_app()
    main_window.show_all()
    Gtk.main()
