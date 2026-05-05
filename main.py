from gi import require_version

require_version("Gtk", "3.0")

from gi.repository import Gtk

from app.config import APP_TITLE, WOLFRAM_APP_ID
from app.controllers.solver_controller import SolverController
from app.factories.window_factory import MaterialWindowFactory
from app.models.wolfram_model import WolframSolverModel
from app.services.wolfram_client import WolframClient
from app.views.main_view import MainView
from app.views.solver_workspace import SolverWorkspace

def build_app() -> MainView:
    client = WolframClient(app_id=WOLFRAM_APP_ID)
    model = WolframSolverModel(client)
    factory = MaterialWindowFactory()
    view = MainView(title=APP_TITLE)

    view.controllers: list[SolverController] = []

    def attach_controller(workspace: SolverWorkspace) -> None:
        controller = SolverController(
            model=model,
            main_view=workspace,
            component_factory=factory,
        )
        workspace.connect_signals(controller)
        view.controllers.append(controller)

    attach_controller(view.workspace)

    def create_new_tab() -> None:
        new_workspace = view.add_solver_tab()
        attach_controller(new_workspace)
        view.show_all()

    view.set_new_tab_handler(create_new_tab)
    return view


if __name__ == "__main__":
    main_window = build_app()
    main_window.show_all()
    Gtk.main()
