"""
IRC protocol commands.
"""

from irctokens import build as _build


class IRCCommands:
    def user(self, username, mode=0, unused='*', realname=None):
        """Create a new user."""
        if not realname:
            realname = username
        data = _build("USER", [username, str(mode), unused, realname])
        self.send(data)
        self.username = username

    def nick(self, nickname):
        """Set the nick."""
        data = _build("NICK", [nickname])
        self.send(data)
        self.nickname = nickname

    def join(self, channel, key=None):
        """Join a channel."""
        args = [channel]
        if key:
            args.append(key)
        self.send(_build("JOIN", args))
        if channel in self._channels:
            self.channels[channel] = self._channels.pop(channel)
        else:
            self.channels[channel] = {'messages': [], 'users': []}

    def msg(self, target, message):
        """Send a message to a target."""
        data = _build("PRIVMSG", [target, message])
        if target not in self.channels:
            self.logger.warning("Target not in channels, joining: %s", target)
            self.join(target)

        self.channels[target]['messages'].append(message)
        self.send(data)

    def part(self, channel, message=None):
        """Part a channel."""
        args = [channel]
        if message:
            args.append(message)
        self.send(_build("PART", args))
        self._channels[channel] = self.channels.pop(channel)

    def pong(self, server):
        """Respond to a ping."""
        data = _build("PONG", [server])
        self.send(data, quiet=True)

    def quit(self, message=None):
        """Quit the server."""
        if message:
            data = _build("QUIT", [message])
        else:
            data = _build("QUIT")
        self.send(data)
        self.running.clear()

