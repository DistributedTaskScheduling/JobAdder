"""
This module contains classes and definitions related to handling
ServerMessages.
"""

from ja.common.proxy.message_handler import MessageHandler


class ServerMessageHandler(MessageHandler):
    """
    ServerMessageHandler receives ServerMessages and performs the corresponding
    actions on the server.
    """
