class JobCenter:
    """
    Main class for the central server daemon. Contains singleton objects of the
    following classes: ServerCommandHandler, Database, Scheduler, Dispatcher,
    Notifier, HttpServer.
    """

    def __init__(self) -> None:
        """!
        Initialize the JobAdder server daemon.
        This includes:
        1. Parsing the command line arguments and the configuration file.
        2. Connecting to the configured database.
        3. Initializing the scheduler and the dispatcher.
        4. Starting the web server and the email notifier.
        """

    def run(self) -> None:
        """
        Run the main loop of the daemon and listen for incoming requests over the local socket.
        """
