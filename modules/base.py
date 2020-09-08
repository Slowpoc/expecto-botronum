"""base.py
    contains the base module
    by Annika"""

import threading

import config
import core

class Module:
    """Represents a module, which may contain several commands
    """
    def __init__(self) -> None:
        self.commands = {
            "ping": self.ping, "owo": self.owo, "uwu": self.uwu, "timer": self.timer,
            "help": self.help, "commands": self.help, "guide": self.help
        }

    def ping(self, message: core.BotMessage) -> None:
        """Ping: replies "Pong!"

        Arguments:
            message {Message} -- the Message object that invoked the command
        """
        message.respond("Pong!")

    def owo(self, message: core.BotMessage) -> None:
        """owo: replaces vowels with owo faces

        Arguments:
            message {Message} -- the Message object that invoked the command
        """
        text = config.separator.join(message.arguments[1:])
        for vowel in list("AaEeIiOoUu"):
            text = text.replace(vowel, f"{vowel}w{vowel}")
        message.respond(text)


    def uwu(self, message: core.BotMessage) -> None:
        """uwu: turns English into weird anime language

        Arguments:
            message {Message} -- the Message object that invoked the command
        """
        text = config.separator.join(message.arguments[1:])
        uwuRules = {'r': 'w', 'l': 'w', 'R': 'W', 'L': 'W'}
        for key in uwuRules:
            text = text.replace(key, uwuRules[key])
        message.respond(text)

    def timer(self, message: core.BotMessage) -> None:
        """timer: evaluates the given Python expression

        Arguments:
            message {Message} -- the Message object that invoked the command
        """
        if len(message.arguments) not in range(1, 4):
            message.respond(f"Usage: ``{config.commandCharacter}timer <duration>, <optional message>``")
            return
        response = "/wall " if message.type == 'pm' or message.connection.this.can('wall', message.room) else ""
        response += message.arguments[2] if len(message.arguments) > 2 else f"Timer set by {message.sender.name} is up"

        try:
            duration = float(message.arguments[1])
        except ValueError:
            message.respond(f"{message.arguments[1]} isn't a valid duration")
            return
        threading.Timer(duration, message.respond, args=[response]).start()

    def help(self, message: core.BotMessage) -> None:
        """Help

        Arguments:
            message {Message} -- the Message object that invoked the command
        """
        return message.respond(f"Expecto Botronum guide: https://github.com/AnnikaCodes/expecto-botronum/blob/master/README.md#commands")

    def __str__(self) -> str:
        """String representation of the Module

        Returns:
            string -- representation
        """
        return f"Base module: provides basic bot functionality. Commands: {', '.join(self.commands.keys())}"
