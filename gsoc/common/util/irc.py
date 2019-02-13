from random import Random

from fredirc import BaseIRCHandler
from fredirc import Err
from fredirc import IRCClient

import gsoc.settings as config

class ModIRCClient(IRCClient):

    def __init__(self, handler, nick, server, message):
        IRCClient.__init__(self, handler, nick, server)
        self.message = message

class CommandBot(BaseIRCHandler):

    def handle_register(self):
        self.client.join(config.IRC_CHANNEL)
        self.client.send_message(config.IRC_CHANNEL, self.client.message)
        self.client.part("Goodbye!", config.IRC_CHANNEL)

    def handle_own_part(self, channel):
        self.client.terminate()

    def handle_error(self, num, **params):
        if num == Err.NICKNAMEINUSE:
            new_nick = params['nick'] + str(Random().randint(1, 9))
            self.client.register(nick = new_nick)

def send_irc_msg(message):
    client = ModIRCClient(CommandBot(), config.BOT_NICK, config.IRC_SERVER, message)
    client.run()