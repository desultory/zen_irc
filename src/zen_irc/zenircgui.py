
from zenlib.logging import loggify
from .zenircclient import ZenIRCClient

from PyQt6.QtWidgets import QMainWindow, QLabel, QLineEdit, QVBoxLayout, QWidget, QComboBox


@loggify
class ZenIRCGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZenIRC")

        self.display_label = QLabel()
        self.input_box = QLineEdit()
        self.input_box.returnPressed.connect(self.process_input)
        self.channel_selector = QComboBox()
        self.channel_selector.currentIndexChanged.connect(self.update_channels)

        layout = QVBoxLayout()
        layout.addWidget(self.channel_selector)
        layout.addStretch()
        layout.addWidget(self.display_label)
        layout.addWidget(self.input_box)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.client = ZenIRCClient(logger=self.logger, display_label=self.display_label)

        self.update_channels()

    def update_channels(self, *args, **kwargs):
        for channel in self.client.channels:
            if self.channel_selector.findText(channel) == -1:
                self.channel_selector.addItem(channel)

    def process_input(self):
        text = self.input_box.text()
        self.input_box.clear()
        self.client.msg('#zen-test', text)
        self.client.update_gui()

    def closeEvent(self, event):
        self.client.stop()
        super().closeEvent(event)
