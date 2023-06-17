"""UI App"""

from pathlib import Path

from ttkthemes import ThemedTk

from openai_helper.config import Configuration
from openai_helper.ui.main_frame import MainFrame


class App(ThemedTk):
    """Main application controller"""

    def __init__(self, configuration_path: str | Path | None = None):
        super().__init__()
        self.configuration = Configuration(configuration_path)
        self.title("OpenAI Helper")
        self.attributes("-zoomed", True)
        self._create_widgets()

    def _create_widgets(self):
        """Create all widgets"""
        self.main_frame = MainFrame(self)
