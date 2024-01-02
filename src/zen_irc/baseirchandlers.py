"""
Handlers for Basic IRC events.
"""


class BaseIRCHandlers:
    def handle_PING(self, msg):
        """ Respond to PING messages. """
        self.pong(msg.params[0])

    def handle_JOIN(self, msg):
        """ Handle JOIN messages. """
        self.logger.info("[%s] Joined channel: %s." % (msg.source, msg.params[0]))
        self.channels[msg.params[0]]['joined'].set()

    def handle_NICK(self, msg):
        """ Handle NICK messages. """
        if msg.params[0] == self.nickname:
            self.logger.debug("Server registered nickname: %s." % msg.params[0])
        self.logger.info("[%s] Changed nick to: %s." % (msg.source, msg.params[0]))

    def handle_NOTICE(self, msg):
        """ Handle NOTICE messages. """
        self.logger.info("[%s] NOTICE: %s." % (msg.source, msg.params[1]))

    def handle_MODE(self, msg):
        """ Handle MODE messages. """
        self.logger.info("[%s] Your mode is: %s" % (msg.source, msg.params[1]))
        self.mode = msg.params[1]

    def handle_PRIVMSG(self, msg):
        """ Handle PRIVMSG messages. """
        self.logger.info("[%s] %s : %s" % (msg.params[0], msg.source, msg.params[1]))
        self.message_queue.put(msg)

    def handle_PART(self, msg):
        """ Handle PART messages. """
        if len(msg.params) > 1:
            self.logger.info("[%s] User parted channel: %s (%s)" % (msg.source, msg.params[0], msg.params[1]))
        else:
            self.logger.info("[%s] User parted channel: %s" % (msg.source, msg.params[0]))
        if msg.hostmask.nickname != self.nickname:
            self.channels[msg.params[0]]['users'].remove(msg.source)

    def handle_QUIT(self, msg):
        """ Handle QUIT messages. """
        self.logger.info("[%s] Quit: %s." % (msg.source, msg.params[0]))
        self.running.clear()

    def handle_ERROR(self, msg):
        """ Handle ERROR messages. """
        self.logger.error("[%s] Error: %s." % (msg.source, msg.params[0]))
        self.running.clear()
