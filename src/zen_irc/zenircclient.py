from zen_irc import ZenIRC


class ZenIRCClient(ZenIRC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run()

    def handle_PRIVMSG(self, msg):
        """ Handle PRIVMSG messages."""
        print(f"[{msg.params[0]}] {msg.source}: {msg.params[1]}")
