"""
Handlers for IRC events.
"""


def handle_PING(self, msg):
    """ Respond to PING messages. """
    self.pong(msg.params[0])


def handle_JOIN(self, msg):
    """ Handle JOIN messages. """
    self.logger.info("[%s] Joined channel: %s." % (msg.source, msg.params[0]))
    self.channels[msg.params[0]] = {}


def handle_NOTICE(self, msg):
    """ Handle NOTICE messages. """
    self.logger.info("[%s] NOTICE: %s." % (msg.source, msg.params[1]))


def handle_MODE(self, msg):
    """ Handle MODE messages. """
    self.logger.info("[%s] Your mode is: %s" % (msg.source, msg.params[1]))
    self.mode = msg.params[1]


def handle_PRIVMSG(self, msg):
    """ Handle PRIVMSG messages. """
    self.logger.info("[%s] %s" % (msg.source, msg.params[1]))


def handle_PART(self, msg):
    """ Handle PART messages. """
    self.logger.info("[%s] User parted channel: %s (%s)" % (msg.source, msg.params[0], msg.params[1]))
    self.logger.error(self.channels)
    self.channels[msg.params[0]]['users'].remove(msg.source)


def handle_QUIT(self, msg):
    """ Handle QUIT messages. """
    self.logger.info("[%s] Quit: %s." % (msg.source, msg.params[0]))
    self.running.clear()


def handle_ERROR(self, msg):
    """ Handle ERROR messages. """
    self.logger.error("[%s] Error: %s." % (msg.source, msg.params[0]))
    self.running.clear()


def handle_001(self, msg):
    """ Handle 001 messages. """
    self.logger.info("[%s] Welcome message: %s." % (msg.source, msg.params[1]))
    self.server_info["welcome_message"] = msg.params[1]


def handle_002(self, msg):
    """ Handle 002 messages. """
    self.logger.info("[%s] Your host is: %s." % (msg.source, msg.params[1]))
    self.server_info["host"] = msg.params[1]


def handle_003(self, msg):
    """ Handle 003 messages. """
    self.logger.info("[%s] Server creation time: %s." % (msg.source, msg.params[1]))
    self.server_info["creation_time"] = msg.params[1]


def handle_004(self, msg):
    """ Handle 004 messages. """
    self.logger.debug("[%s] Server info: %s." % (msg.source, msg.params))


def handle_005(self, msg):
    """ Handle 005 messages. """
    supported_features = msg.params[1:-1]
    self.logger.debug("[%s] Supported features: %s." % (msg.source, " ".join(supported_features)))
    self.server_info["supported_features"] += supported_features


def handle_250(self, msg):
    """ Handle 250 messages. """
    msg_bits = msg.params[1].split(" ")
    self.server_info["max_connection_count"] = int(msg_bits[3])
    self.server_info["max_client_count"] = int(msg_bits[4][1:])
    self.server_info["max_connections_received"] = int(msg_bits[6][1:])
    self.logger.info("[%s] Highest connection count: %s (%s clients) - total connections: %s." % (
        msg.source, msg_bits[3], msg_bits[4][1:], msg_bits[6][1:]
    ))


def handle_251(self, msg):
    """ Handle 251 messages. """
    msg_bits = msg.params[1].split(" ")
    self.server_info["user_count"] = int(msg_bits[2])
    self.server_info["invisible_count"] = int(msg_bits[5])
    self.server_info["server_count"] = int(msg_bits[8])

    self.logger.info("[%s] There are %s users and %s invisible on %s servers." % (
        msg.source, msg_bits[2], msg_bits[5], msg_bits[8]
    ))


def handle_252(self, msg):
    """ Handle 252 messages. """
    self.logger.info("[%s] Operators online: %s" % (msg.source, msg.params[1]))
    self.server_info["operator_count"] = int(msg.params[1])


def handle_253(self, msg):
    """ Handle 253 messages. """
    self.logger.info("[%s] Unknown connections: %s" % (msg.source, msg.params[1]))
    self.server_info["unknown_count"] = int(msg.params[1])


def handle_254(self, msg):
    """ Handle 254 messages. """
    self.logger.info("[%s] Channels: %s" % (msg.source, msg.params[1]))
    self.server_info["channel_count"] = int(msg.params[1])


def handle_255(self, msg):
    """ Handle 255 messages. """
    msg_bits = msg.params[1].split(" ")
    self.server_info["local_client_count"] = int(msg_bits[2])
    self.server_info["local_server_count"] = int(msg_bits[5])

    self.logger.info("[%s] There are %s client on %s server(s)." % (
        msg.source, msg_bits[2], msg_bits[5]
    ))


def handle_265(self, msg):
    """ Handle 265 messages. """
    self.server_info["local_user_count"] = int(msg.params[1])
    self.server_info["max_local_user_count"] = int(msg.params[2])
    self.logger.info("[%s] Local user count: %s / %s" % (msg.source, msg.params[1], msg.params[2]))


def handle_266(self, msg):
    """ Handle 266 messages. """
    self.server_info["global_user_count"] = int(msg.params[1])
    self.server_info["max_global_user_count"] = int(msg.params[2])
    self.logger.info("[%s] Global user count: %s / %s" % (msg.source, msg.params[1], msg.params[2]))


def handle_353(self, msg):
    """ Handle 353 messages. """
    channel = msg.params[2]
    users = msg.params[3].split(" ")
    self.logger.debug("[%s] Users in channel %s: %s" % (msg.source, channel, " ".join(users)))
    if 'users' not in self.channels[channel]:
        self.channels[channel]['users'] = users
    else:
        self.channels[channel]['users'] += users


def handle_366(self, msg):
    """ Handle 366 messages. """
    self.logger.info("[%s] Users in %s: %s" % (msg.source, msg.params[1],
                                               " ".join(self.channels[msg.params[1]]['users'])))


def handle_375(self, msg):
    """ Handle 375 messages. """
    self.motd_start.set()
    self.server_info["motd_header"] = msg.params[1]
    self.server_info["motd"] = []
    self.logger.info("[%s] Message of the day header: %s" % (msg.source, msg.params[1]))


def handle_372(self, msg):
    """ Handle 372 messages. """
    if not self.motd_start.is_set():
        self.logger.warning("[%s] Received MOTD line before MOTD header." % msg.source)
        self.motd_start.set()
        self.server_info["motd_header"] = ""
        self.server_info["motd"] = []
    self.server_info["motd"].append(msg.params[1])
    self.logger.debug("[%s] MOTD: %s" % (msg.source, msg.params[1]))


def handle_376(self, msg):
    """ Handle 376 messages. """
    self.motd_start.clear()
    self.logger.info("[%s] MOTD: %s\n%s" % (msg.source, self.server_info["motd_header"],
                                            "\n".join(self.server_info["motd"])))


def handle_477(self, msg):
    """ Handle 477 messages. """
    self.logger.warning("[%s(%s)] %s" % (msg.source, msg.params[1], msg.params[2]))
    self.channels[msg.params[1]]['failed'] = True


