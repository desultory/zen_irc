from zenlib.logging import ClassLogger
from zenlib.threading import ZenThread

from .baseirchandlers import BaseIRCHandlers
from .extendedirchandlers import ExtendedIRCHandlers
from .irccommands import IRCCommands

from tomllib import load
from socket import socket, AF_INET, SOCK_STREAM, timeout
from ssl import wrap_socket
from irctokens import StatefulDecoder, StatefulEncoder
from threading import Event
from queue import Queue


class ZenIRC(ClassLogger, BaseIRCHandlers, ExtendedIRCHandlers, IRCCommands):
    def __init__(self, config="config.toml", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_file = config
        self.load_config()

        self.encoder = StatefulEncoder()
        self.decoder = StatefulDecoder()
        self.loop_thread = ZenThread(target=self.mainloop, looping=True, logger=self.logger)
        self.channels = {}
        self.message_queue = Queue()

        self.stop_cmd = ['QUIT']
        self.running = Event()
        self.initialized = Event()

    def load_config(self):
        """ Loads the config file from self.config_file. """
        self.logger.info('Loading config file: %s' % self.config_file)
        with open(self.config_file, 'rb') as f:
            self.config = load(f)

        self.logger.debug('Loaded config: %s' % self.config)

    def send(self, msg, quiet=False):
        """ Sends a message to the IRC server. """
        self.logger.debug('Encoding message: %s' % msg)
        self.encoder.push(msg)
        while pending_msg := self.encoder.pending():
            log_level = 20 if quiet else 10
            self.logger.log(log_level, 'Sending message: %s' % pending_msg.decode().strip())
            self.encoder.pop(self.irc_socket.send(pending_msg))

    def connect(self):
        """ Connects to the specified IRC server. """
        self._socket = socket(AF_INET, SOCK_STREAM)
        self.logger.debug('Created socket: %s' % self._socket)
        self.irc_socket = wrap_socket(self._socket)
        self.logger.debug('Wrapped socket: %s' % self.irc_socket)
        self.irc_socket.settimeout(1)

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
            self.logger.warning('Received stop command: %s' % line.command)
            self.stop()

    def connection_init(self):
        """ Initializes the connection to the IRC server. """
        self.connect()
        self.user(self.config['user'])
        self.nick(self.config['user'])
        self.server_info = {'supported_features': []}
        self.motd_start = Event()

        # Add a hook to handle 376 (end of MOTD) and then remove it
        # This is so we can wait for the end of the MOTD before joining channels
        pre_stop_cmd = self.stop_cmd.copy()
        self.stop_cmd = ['376']
        # Run the mainloop manually, since we're not actually running the client yet
        self.loop_thread.start()
        self.loop_thread.join()
        self.stop_cmd = pre_stop_cmd

        self.logger.info("[%s] Supported features: %s" % (self.config['server'], self.server_info['supported_features']))

        for channel in self.config.get('channels'):
            self.join(channel)
            self.logger.info("[%s] Joined channel: %s" % (self.config['server'], channel))

        self.initialized.set()

    def run(self):
        """ Runs the client. """
        if not self.initialized.is_set():
            self.connection_init()
        try:
            self.loop_thread.start()
        except KeyboardInterrupt:
            self.logger.warning("Received keyboard interrupt, sending QUIT")
            self.quit(message="Keyboard interrupt")
            self.run()

    def stop(self):
        self.loop_thread.loop.clear()

    def mainloop(self):
        """ Main loop for the client. """
        try:
            data = self.irc_socket.recv(1024)
        except timeout:
            return
        self.logger.log(5, 'Received data: %s' % data)
        lines = self.decoder.push(data)
        if lines is None:
            self.logger.warning("No lines returned from decoder, connection may have been closed.")
            self.stop()

        for line in lines:
            self.process_line(line)

        self.loop_actions()

    def loop_actions(self):
        self.process_messages()

    def process_message(self, msg):
        """ Processes a message from the message queue. """
        self.logger.debug('Processing message: %s' % msg)
        print(f"[{msg.params[0]}] <{msg.source}> {msg.params[1]}")

    def process_messages(self):
        """ Processes messages from the message queue. """
        while not self.message_queue.empty():
            self.process_message(self.message_queue.get())


