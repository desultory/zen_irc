from zen_irc import ZenIRC


class ZenIRCClient(ZenIRC):
    def __init__(self, display_label=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.display_label = display_label
        self.run()

    def update_gui(self):
        if self.display_label:
            message_str = ''
            for channel in self.channels:
                for sender, message in self.channels[channel].get('messages'):
                    sender = sender or self.nick
                    message_str += f"[{channel}] {sender}: {message}\n"
            self.display_label.setText(message_str)

    def process_message(self, msg):
        channel = msg.params[0]
        message = msg.params[1]
        sender = msg.source
        self.channels[channel]['messages'].append((sender, message))
        self.update_gui()
