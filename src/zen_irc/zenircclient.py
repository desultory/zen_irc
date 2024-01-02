from zen_irc import ZenIRC
from queue import Queue


class ZenIRCClient(ZenIRC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_queue = Queue()
        self.run()

    def handle_PRIVMSG(self, msg):
        """ Handle PRIVMSG messages."""
        self.logger.debug("Got message: %s" % (msg))
        self.message_queue.put(msg)

    def loop_actions(self):
        """ Actions to perform in the loop. """
        # Check for messages in the queue
        if not self.message_queue.empty():
            print(self.message_queue.get())
        else:
            self.logger.debug("Message queue is empty.")
