#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Emanuele"
__version__ = "0.1.a"
__email__ = "ema.muna95@gmail.com"
__status__ = "Development"

try:
    # For Python 3.0+
    from urllib.request import urlopen
except ImportError:
    # Fall back to python 2.0+
    from urllib2 import urlopen

import json
from time import sleep
import urllib
import urllib2
import re


class StaseraTVBot:
    """Just a class for a telegramBot used for sending TVGuide.

    Internal attributes:
    token -- It's your token bot
    botname -- Name used to send messages
    """

    def __init__(self, token, botname):
        """Initialize a new BOT identified by token and botname.
        """

        self.token = token
        self.name = botname

    def start(self):
        """Start the BOT.
        """

        self.checknew(1)

    def runcommand(self, command):
        """Execute a command using Telegram API, learn more on Telegram Documentation.

        Keyword arguments:
        command: Command to execute (https://core.telegram.org/bots/api)
        """

        api = 'https://api.telegram.org/bot'
        json_url = api + self.token + '/' + command
        url = urlopen(json_url)
        string = url.read()
        result = json.loads(string)  # result is a dict
        url.close()
        return result

    def getlastmessage(self):
        """Receive incoming updates

        TODO: Need to improve the error handling and the structure of the method
        """
        try:
            result = self.runcommand('getUpdates')
            messages = result['result']
            n = len(messages)
            if n != 0:
                n -= 1  # n is the length of the dict, need to take last element
                message = {'message_id': messages[n]['message']['message_id'],
                           'chat_id': messages[n]['message']['chat']['id'],
                           'text': messages[n]['message']['text']}
            else:
                message = {'message_id': -1}
            return message
        except:
            return {'message_id': -1}

    def sendtextmessage(self, text, chat_id):
        command = 'sendMessage?chat_id=' + str(chat_id) + '&text=' + text
        self.runcommand(command)

    def parsecommand(self, message):
        command = message['text'][1:].split(' ', 1)  # Skip first char, then read the 2 strings (/command [option])
        command[0] = command[0].lower()
        if command[0] == 'staseraintv':
            print "aaa"
            channels = ['Rai 1', 'Rai 2', 'Rai 3', 'Rai 4', 'Canale 5', 'Italia 1', 'Rete 4']
            plot, titles = self.getshow()
            hellomesg = self.name+" ti augura una buona visione :-)!"
            self.sendtextmessage(hellomesg, message['chat_id'])
            for splot, stitle, channel in zip(plot, titles, channels):
                string = urllib.quote_plus("Canale: %s\nTitolo:\n%s\nTrama:\n%s" % (channel, stitle, splot))
                self.sendtextmessage(string, message['chat_id'])

    def checknew(self, time):
        """Check every [time] secs for incoming messages.

        Keyword arguments:
        time -- Time to wait for a new check. (You can use floating numbers for ms, ie: 0.05)

        """
        lastread = 0
        while 1:
            lastmessage = self.getlastmessage()
            if lastmessage['message_id'] > lastread:  # New message
                self.parsecommand(lastmessage)
                lastread = lastmessage['message_id']
            sleep(time)

    @staticmethod
    def getshow():
        """Return the TVguide parsing data from staseraintv.com

        Keyword arguments:
        real -- the real part (default 0.0)
        """
        weburl = 'http://www.staseraintv.com'
        data = urllib2.urlopen(weburl)
        htmltext = data.read()
        regex = '<span style=" font-weight: normal">(.+?)</span>'  # regex per titoli film
        regex2 = '<span style="font-weight: normal">(.+?)<a'  # Regex per nome canali
        pattern = re.compile(regex, re.IGNORECASE | re.DOTALL)
        pattern2 = re.compile(regex2, re.IGNORECASE | re.DOTALL)
        titles = re.findall(pattern, htmltext)
        plot = re.findall(pattern2, htmltext)
        titles = map(lambda s: s.strip(), titles)
        plot = map(lambda s: s.strip(), plot)
        return plot, titles
