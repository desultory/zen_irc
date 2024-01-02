from zenlib.logging import loggify
from .zenircclient import ZenIRCClient

from PyQt6.QtWidgets import QMainWindow, QLabel, QLineEdit, QVBoxLayout, QWidget, QComboBox, QScrollArea
from PyQt6.QtCore import pyqtSignal, Qt


@loggify
class ZenIRCGUI(QMainWindow):
    update_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZenIRC")

        self.update_signal.connect(self.update_gui)
        self.channel_selector = QComboBox()
        self.channel_selector.currentIndexChanged.connect(self.update_channels)

        display_box = QScrollArea()
        display_box.setWidgetResizable(True)
        display_layout = QVBoxLayout()
        display_layout.addStretch()
        display_box.setLayout(display_layout)
        self.display_label = QLabel()
        self.display_label.setWordWrap(True)
        self.display_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        display_layout.addWidget(self.display_label)

        self.input_box = QLineEdit()
        self.input_box.returnPressed.connect(self.process_input)

        layout = QVBoxLayout()
        layout.addWidget(self.channel_selector)
        layout.addWidget(display_box)
        layout.addWidget(self.input_box)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.client = ZenIRCClient(logger=self.logger, update_signal=self.update_signal)
        self.update_signal.emit()

    def update_gui(self):
        self.update_channels()
        self.update_display()

    def update_display(self):
        if not self.client.active_channel:
            return
        channel = self.client.channels.get(self.client.active_channel) or self.client._channels[self.client.active_channel]
        label_text = ''
        for message in channel['messages']:
            if isinstance(message, str):
                label_text += f"{self.client.nickname}: {message}\n"
                continue
            label_text += f"{message.hostmask.nickname}: {message.params[1]}\n"
        self.display_label.setText(label_text)
        self.channel_selector.setCurrentText(self.client.active_channel)

    def update_channels(self, channel=None):
        if channel is not None:
            self.client.active_channel = self.channel_selector.currentText()
            self.logger.info("Updated active channel: %s", self.client.active_channel)
            self.update_display()

        for channel in self.client.channels:
            if self.channel_selector.findText(channel) == -1:
                self.channel_selector.addItem(channel)

    def process_input(self):
        text = self.input_box.text()
        self.input_box.clear()
        if text.startswith('/'):
            cmd, *args = text[1:].split(' ')
            try:
                getattr(self.client, cmd.lower())(*args)
            except AttributeError:
                self.logger.error("Unknown command: %s", cmd)
        else:
            self.client.msg(self.client.active_channel, text)
        self.update_signal.emit()

    def closeEvent(self, event):
        self.client.stop()
        super().closeEvent(event)
