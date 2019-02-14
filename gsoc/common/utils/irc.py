from random import randint

from fredirc import BaseIRCHandler
from fredirc import Err
from fredirc import IRCClient

import gsoc.settings as config

class ModIRCClient(IRCClient):

    def __init__(self, handler, nick, server, messages):
        IRCClient.__init__(self, handler, nick, server)
        self.messages = messages

class CommandBot(BaseIRCHandler):

    def handle_register(self):
        for message in self.client.messages:
            self.client.send_private_message(config.RECEIVER, message)
        self.client.quit()

    def handle_disconnect(self):
        self.client.terminate()

    def handle_error(self, num, **params):
        if num == Err.NICKNAMEINUSE:
            new_nick = params['nick'] + str(randint(1, 9))
            self.client.register(nick = new_nick)

def send_message(messages):
    client = ModIRCClient(CommandBot(), config.BOT_NICK, config.IRC_SERVER, messages)
    client.set_log_level(5)
    client.run()
