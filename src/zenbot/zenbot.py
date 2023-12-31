from zenlib.logging import loggify

from tomllib import load
from socket import socket, AF_INET, SOCK_STREAM
from ssl import wrap_socket
from irctokens import StatefulDecoder, StatefulEncoder
from importlib import import_module
from functools import partial
from threading import Event


class EndRunloopSignal(Exception):
    """ Raised when processing should end. """
    pass


@loggify
class ZenBot:
    def __init__(self, config="config.toml", *args, **kwargs):
        self.config_file = config
        self.load_config()
        self.load_commands()
        self.load_handlers()

        self.encoder = StatefulEncoder()
        self.decoder = StatefulDecoder()

        self.stop_cmd = ['QUIT']
        self.running = Event()
        self.initialized = Event()

    def load_config(self):
        """ Loads the config file from self.config_file. """
        self.logger.info('Loading config file: %s' % self.config_file)
        with open(self.config_file, 'rb') as f:
            self.config = load(f)
        self.logger.debug('Loaded config: %s' % self.config)

        if 'channels' not in self.config:
            raise ValueError('No channels specified in config file')

    def _import_callables(self, module):
        """ Imports all callables from a module unless they start with an underscore."""
        raw_module = import_module(module)
        return [getattr(raw_module, command) for command in dir(raw_module) if callable(getattr(raw_module, command)) and not command.startswith('_')]

    def load_handlers(self):
        """ Loads the handlers module. """
        for handler in self._import_callables('zenbot.handlers'):
            if getattr(self, handler.__name__, None):
                raise ValueError('Handler already exists: %s' % handler.__name__)
            if not handler.__name__.startswith('handle_'):
                raise ValueError('Handler does not start with "handle_": %s' % handler.__name__)
            func = partial(handler, self)
            setattr(self, handler.__name__, func)
            self.logger.debug('Loaded handler: %s' % handler.__name__)

    def load_commands(self):
        """ Loads defined IRC commands from the commands module. """
        for command in self._import_callables('zenbot.commands'):
            if getattr(self, command.__name__, None):
                raise ValueError('Command already exists: %s' % command.__name__)
            func = partial(command, self)
            setattr(self, command.__name__, func)
            self.logger.debug('Loaded command: %s' % command.__name__)

    def send(self, msg):
        """ Sends a message to the IRC server. """
        self.logger.debug('Encoding message: %s' % msg)
        self.encoder.push(msg)
        while pending_msg := self.encoder.pending():
            self.logger.info('Sending message: %s' % pending_msg.decode().strip())
            self.encoder.pop(self.irc_socket.send(pending_msg))

    def connect(self):
        """ Connects to the specified IRC server. """
        self._socket = socket(AF_INET, SOCK_STREAM)
        self.logger.debug('Created socket: %s' % self._socket)
        self.irc_socket = wrap_socket(self._socket)
        self.logger.debug('Wrapped socket: %s' % self.irc_socket)

        self.irc_socket.connect((self.config['server'], self.config['port']))
        self.logger.info('Connected to %s:%s' % (self.config['server'], self.config['port']))

    def process_line(self, line):
        """ Processes a line from the IRC server. """
        self.logger.debug('Processing line: %s' % line)
        if handler := getattr(self, f'handle_{line.command}', None):
            handler(line)
        else:
            self.logger.warning('[%s] Unhandled line: %s' % (line.command, line))

        if line.command in self.stop_cmd:
            raise EndRunloopSignal('Received stop command: %s' % line.command)

    def connection_init(self):
        """ Initializes the connection to the IRC server. """
        self.connect()
        self.user(self.config['user'])
        self.nick(self.config['user'])
        self.server_info = {'supported_features': []}
        self.channels = {}
        self.motd_start = Event()

        self.logger.info('Connected to %s:%s' % (self.config['server'], self.config['port']))

        pre_stop_cmd = self.stop_cmd.copy()
        self.stop_cmd = ['376', 'MODE']
        self.runloop()
        self.stop_cmd = pre_stop_cmd

        self.logger.info("[%s] Supported features: %s" % (self.config['server'], self.server_info['supported_features']))

        for channel in self.config['channels']:
            self.join(channel)

        self.initialized.set()

    def run(self):
        """ Runs the client. """
        if not self.initialized.is_set():
            self.connection_init()
        try:
            self.runloop()
        except KeyboardInterrupt:
            self.logger.warning("Received keyboard interrupt, sending QUIT")
            self.quit(message="Keyboard interrupt")
            self.run()

    def runloop(self):
        """ Main runloop for the bot. """
        self.logger.debug('Starting runloop')
        self.running.set()
        while data := self.irc_socket.recv(1024):
            stop_signal = False
            if not self.running.is_set():
                stop_signal = True
            self.logger.log(5, 'Received data: %s' % data)
            lines = self.decoder.push(data)
            if lines is None:
                self.logger.warning("No lines returned from decoder, connection may have been closed.")
                break

            for line in lines:
                try:
                    self.process_line(line)
                except EndRunloopSignal as e:
                    self.logger.warning("Stopping runloop: %s" % e)
                    stop_signal = True

            if stop_signal:
                break

