from zen_irc import ZenIRC


class ZenIRCClient(ZenIRC):
    """
    Add an active_channel attribute to the ZenIRC class.
    Overrides the JOIN handler to set the active_channel and update the gui.
    Add the update signal option, which allows the client to update the gui.
    """
    def __init__(self, update_signal=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_channel = None
        self.update_signal = update_signal
        self.run()

    def process_message(self, msg):
        channel = msg.params[0]
        self.channels[channel]['messages'].append(msg)
        if self.update_signal:
            self.update_signal.emit()

    def handle_JOIN(self, msg):
        """ Set the current_channel. """
        super().handle_JOIN(msg)
        channel = msg.params[0]
        self.active_channel = channel
        if self.update_signal:
            self.update_signal.emit()
