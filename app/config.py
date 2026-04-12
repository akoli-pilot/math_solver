import os

APP_TITLE = "Math Solver"
WOLFRAM_ENDPOINT = "https://api.wolframalpha.com/v2/query"
WOLFRAM_APP_ID = os.getenv("WOLFRAM_APP_ID", "DEMO")
REQUEST_TIMEOUT = int(os.getenv("WOLFRAM_TIMEOUT", "20"))
MAX_DISPLAY_ELEMENTS = int(os.getenv("MAX_DISPLAY_ELEMENTS", "80"))
