import requests
from discord_hooks import Webhook
class Hooker(object):
    """Webhook for pingers"""
    def __init__(self, channel):
        self.channel = channel

    def ping(self, message):
        channel = self.channel
        msg = Webhook(channel,msg=message)
        msg.post()
