from zenlib.logging import ClassLogger, log_call

from .baseirchandlers import BaseIRCHandlers
from .extendedirchandlers import ExtendedIRCHandlers
from .irccommands import IRCCommands

from tomllib import load
from irctokens import StatefulDecoder, StatefulEncoder
from threading import Event, Lock
from queue import Queue
import asyncio


class ZenIRC(ClassLogger, BaseIRCHandlers, ExtendedIRCHandlers, IRCCommands):
    def __init__(self, config="config.toml", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_file = config
        self.load_config()

        self.encoder = StatefulEncoder()
        self.decoder = StatefulDecoder()
        self.channels = {}
        self._channels = {}  # For removed channels
        self.message_queue = Queue()

        self.stop_cmd = ['QUIT']
        self.send_lock = Lock()
        self.initialized = Event()

    def load_config(self):
        """ Loads the config file from self.config_file. """
        self.logger.info('Loading config file: %s' % self.config_file)
        with open(self.config_file, 'rb') as f:
            self.config = load(f)

        self.logger.debug('Loaded config: %s' % self.config)

    @log_call(20)
    def send(self, msg, quiet=False):
        """ Sends a message to the IRC server. Locks so it works with asyncio. """
        self.logger.debug('Encoding message: %s' % msg)
        with self.send_lock:
            self.encoder.push(msg)
            while pending_msg := self.encoder.pending():
                log_level = 20 if quiet else 10
                self.logger.log(log_level, 'Sending message: %s' % pending_msg.decode().strip())
                self.irc_writer.write(pending_msg)
                self.encoder.clear()

    async def start(self):
        """ Start the IRC connection. """
        if not hasattr(self, 'irc_reader') or not hasattr(self, 'irc_writer'):
            self.logger.info("Initializing connection.")
            await self.connection_init()

        asyncio.create_task(self.reader_loop())
        self.connection_setup()

    def stop(self):
        """ End the event loop. """
        self.logger.info('Stopping event loop.')
        asyncio.get_event_loop().stop()

    async def connection_init(self):
        """ Connects to the specified IRC server. """
        self.irc_reader, self.irc_writer = await asyncio.open_connection(self.config['server'], self.config['port'], ssl=True)
        self.logger.info('Connected to IRC server: %s:%d' % (self.config['server'], self.config['port']))
        self.logger.debug("Reader: %s, Writer: %s" % (self.irc_reader, self.irc_writer))

    def connection_setup(self):
        """ Initializes the connection to the IRC server. """
        self.user(self.config['user'])
        self.nick(self.config['user'])
        self.server_info = {'supported_features': []}

        self.logger.info("[%s] Supported features: %s" % (self.config['server'], self.server_info['supported_features']))

        for channel in self.config.get('channels'):
            self.join(channel)
            self.logger.info("[%s] Joined channel: %s" % (self.config['server'], channel))

        self.initialized.set()

    async def process_line(self, line):
        """ Processes a line from the IRC server. """
        self.logger.debug('Processing line: %s' % line)
        if handler := getattr(self, f'handle_{line.command}', None):
            await handler(line)
        else:
            self.logger.warning('[%s] Unhandled line: %s' % (line.command, line))

        if line.command in self.stop_cmd:
            self.logger.warning('Received stop command: %s' % line.command)
            self.stop()

    async def reader_loop(self):
        """ Loop for the irc_reader. """
        while True:
            self.logger.warning("ASDFASDF")
            data = await self.irc_reader.read(1024)
            if not data:
                self.logger.warning("No data received, connection may have been closed.")
                return self.stop()

            self.logger.log(5, 'Received data: %s' % data)
            lines = self.decoder.push(data)
            if lines is None:
                self.logger.warning("No lines returned from decoder, connection may have been closed.")
                return self.stop()

            for line in lines:
                await self.process_line(line)

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


