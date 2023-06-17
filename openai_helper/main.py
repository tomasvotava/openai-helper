"""Main entrypoint for the openai-helper package"""
import logging

from openai_helper.ui.app import App

logger = logging.getLogger(__name__)


def gui_main():
    """Main entrypoint for the GUI"""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    gui_main()
