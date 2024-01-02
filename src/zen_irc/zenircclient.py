from zen_irc import ZenIRC


class ZenIRCClient(ZenIRC):
    def __init__(self, update_signal=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_signal = update_signal
        self.run()

    def process_message(self, msg):
        channel = msg.params[0]
        message = msg.params[1]
        sender = msg.source
        self.channels[channel]['messages'].append((sender, message))
        if self.update_signal:
            self.update_signal.emit()
