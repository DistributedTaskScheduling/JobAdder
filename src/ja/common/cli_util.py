from abc import abstractmethod
from argparse import ArgumentParser
from io import StringIO
from ja.common.message.base import Response
from ja.common.proxy.remote import Remote
import yaml


class SimpleDaemonCLIInterface:
    def __init__(self) -> None:
        parser = ArgumentParser()
        parser.add_argument("-k", "--kill", help="Shut down the job adder server.", action="store_true")
        args = parser.parse_args()
        if args.kill:
            self._kill_daemon()
        else:
            self.run_main()

    def _kill_daemon(self) -> None:
        # We construct a fake message and send it to the daemon.
        kill_command_dict = {
            "command": {},
            "type_name": "KillCommand"
        }

        response_buffer = StringIO()
        Remote(self.socket_name, StringIO(yaml.dump(kill_command_dict)), response_buffer)
        response = Response.from_string(response_buffer.getvalue())
        print(response.result_string)

    @property
    @abstractmethod
    def socket_name(self) -> str:
        """!
        @return The socket name to connect to if sending KillCommand.
        """
        pass

    @abstractmethod
    def run_main(self) -> None:
        """
        Run the main class of the component.
        """
