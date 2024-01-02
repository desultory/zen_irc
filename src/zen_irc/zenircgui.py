
from zenlib.logging import loggify
from .zenircclient import ZenIRCClient

from PyQt6.QtWidgets import QMainWindow, QLabel


@loggify
class ZenIRCGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ZenIRC")
        self.client = ZenIRCClient(logger=self.logger)
        self.display_label = QLabel()

        self.setCentralWidget(self.display_label)

    def closeEvent(self, *args, **kwargs):
        self.client.stop_mainloop_thread()
