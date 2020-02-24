from ja.common.proxy.command_handler import CommandHandler
from threading import Thread
from typing import Any


class ThreadedCommandHandler(CommandHandler):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._listen_thread = Thread(target=self.main_loop)
        self._listen_thread.daemon = True  # Ensures that the thread is killed when main thread exits
        self._listen_thread.start()
