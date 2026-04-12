# Wolfram Math Solver (Model View Control + Factory Method)

Interactive desktop math solver built with Python + GTK3. Queries are sent to the Wolfram Alpha API and rendered as math element cards in a single main window.

Input uses a scientific calculator style keypad that builds LaTeX expressions with live preview. Equation output is rendered only through LaTeX images

## Architecture

- Model: `app/models/wolfram_model.py`
  - Normalizes Wolfram API data into `MathElement` and `SolverResult`.
- View: `app/views/main_view.py`, `app/views/widgets.py`, `app/views/equation_editor.py`
  - Material-inspired GTK3 UI with card interaction.
- LaTeX Rendering: `app/views/latex_renderer.py`
  - Converts equation into LaTeX rendered transparent images for GTK.
- Controller: `app/controllers/solver_controller.py`
  - Handles user actions, async API calls, and updates view state.
- Factory Method: `app/factories/window_factory.py`
  - `MaterialWindowFactory` creates windows and math element widgets.
- Service: `app/services/wolfram_client.py`
  - Handles API request/response parsing from Wolfram Alpha XML.

## Material Design 3 Notes

The UI applies M3-style tokens and interactions in `app/views/material_theme.css`:
- elevated surface panels with rounded corners
- clear hierarchy (`headline`, `section-title`, status chips)
- expressive color system with surface/container/primary roles
- card based interactive result model
- responsive flow layout that works on compact and wide window sizes

## Requirements

- Python 3.10+
- GTK3 Python bindings (`PyGObject`)
- Matplotlib (LaTeX/mathtext equation rendering)
- Wolfram Alpha API Key

## Setup

```bash
cd math_solver/
python3 -m venv .venv
source .venv/bin/activate
```

Installing `PyGObject` as a system dependency

```bash
sudo apt-get install python3-gi gir1.2-gtk-3.0
```

## Run

```bash
export WOLFRAM_APP_ID="YOUR_API_KEY"
python3 main.py
```

## Usage

1. Build a query with the scientific keypad (numbers, operators, and math functions).
2. Click **Solve**.
3. Review returned math cards and use results to refine the next query.
