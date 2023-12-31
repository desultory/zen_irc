"""
IRC protocol commands.
"""

from irctokens import build as _build


def user(self, username, mode=0, unused='*', realname=None):
    """Create a new user."""
    if not realname:
        realname = username
    data = _build("USER", [username, str(mode), unused, realname])
    self.send(data)
    self.user = username


def nick(self, nickname):
    """Set the nick."""
    data = _build("NICK", [nickname])
    self.send(data)
    self.nick = nickname


def join(self, channel, key=None):
    """Join a channel."""
    args = [channel]
    if key:
        args.append(key)
    data = _build("JOIN", args)
    self.send(data)
    self.channels[channel] = {}


def msg(self, target, message):
    """Send a message to a target."""
    data = _build("PRIVMSG", [target, message])
    self.send(data)


def pong(self, server):
    """Respond to a ping."""
    data = _build("PONG", [server])
    self.send(data)


def quit(self, message=None):
    """Quit the server."""
    if message:
        data = _build("QUIT", [message])
    else:
        data = _build("QUIT")
    self.send(data)
    self.running.clear()

