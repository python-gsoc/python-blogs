import json
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
        for data in self.client.messages:
            commands = parse_data(data)
            for command in commands:
                self.client.send_private_message(config.RECEIVER, command)
        self.client.quit()

    def handle_disconnect(self):
        self.client.terminate()

    def handle_error(self, num, **params):
        if num == Err.NICKNAMEINUSE:
            new_nick = params['nick'] + str(randint(1, 9))
            self.client.register(nick = new_nick)

def parse_data(data):
    """
    parses the message data and returns corresponding commands for the message

    `data` should be in the form of a json: `'{"command": "<command>", "message": "<message>"}'`
    """
    data = json.loads(data)
    chunk_size = 150
    chunks = [data['message'][i:i+chunk_size] for i in range(0, len(data['message']), chunk_size)]
    num_chunks = len(chunks)
    commands = []
    for i in range(num_chunks):
        commands.append('@aka add m{} "echo {}"'.format(i, chunks[i]))

    echo_text = ' '.join(['echo' for i in range(num_chunks)])
    msg_text = ' '.join(['[m{}]'.format(i) for i in range(num_chunks)])
    commands.append('@messageparser add global "{}" [{} {}]'.format(data['command'], echo_text, msg_text))

    for i in range(num_chunks):
        commands.append('@aka remove m{}'.format(i))

    return commands

def send_message(messages):
    """
    sends a set of messages to the receiver on irc after parsing them
    """
    client = ModIRCClient(CommandBot(), config.BOT_NICK, config.IRC_SERVER, messages)
    client.set_log_level(5)
    client.run()
