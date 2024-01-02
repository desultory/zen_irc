"""
IRC protocol commands.
"""

from zenlib.threading import threaded
from threading import Event
from irctokens import build as _build


class IRCCommands:
    def user(self, username, mode=0, unused='*', realname=None):
        """Create a new user."""
        realname = realname or username
        self.send(_build("USER", [username, str(mode), unused, realname]))
        self.username = username

    def nick(self, nickname):
        """Set the nick."""
        self.send(_build("NICK", [nickname]))
        self.nickname = nickname

    def join(self, channel, key=None):
        """Join a channel. Wait for the server to respond if wait is True."""""
        args = [channel, key] if key else [channel]
        self.send(_build("JOIN", args))
        if channel in self._channels:
            self.channels[channel] = self._channels.pop(channel)
        else:
            self.channels[channel] = {'messages': [], 'users': []}
        self.channels[channel]['joined'] = Event()

    @threaded
    def msg(self, target, message):
        """Send a message to a target."""
        data = _build("PRIVMSG", [target, message])
        if target not in self.channels:
            self.join(target)
            self.channels[target]['joined'].wait()
        self.channels[target]['messages'].append(message)
        self.send(data)

    def part(self, channel, message=None):
        """Part a channel."""
        args = [channel, message] if message else [channel]
        self.send(_build("PART", args))
        self.channels[channel]['joined'].clear()
        self._channels[channel] = self.channels.pop(channel)

    def pong(self, server):
        """Respond to a ping."""
        self.send(_build("PONG", [server]), quiet=True)

    def quit(self, message=None):
        """Quit the server."""
        data = _build("QUIT", [message]) if message else _build("QUIT")
        self.send(data)
        self.running.clear()

