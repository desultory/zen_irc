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

    def process_message(self, msg):
        channel = msg.params[0]
        self.channels[channel]['messages'].append(msg)
        if self.update_signal:
            self.update_signal.emit()

    def handle_JOIN(self, msg):
        """ Set the current_channel. """
        super().handle_JOIN(msg)
        if self.update_signal:
            self.update_signal.emit()

    def part(self, channel=None, *args, **kwargs):
        """ Override the part method to set the active_channel. """
        channel = channel or self.active_channel
        super().part(channel, *args, **kwargs)

    def join(self, channel=None, *args, **kwargs):
        """ Override the join method to set the active_channel. """
        channel = channel or self.active_channel
        super().join(channel, *args, **kwargs)
        if self.update_signal:
            self.update_signal.emit()
        self.active_channel = channel
