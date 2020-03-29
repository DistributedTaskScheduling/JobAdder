from ja.common.proxy.remote import Remote
from ja_integration.remote import WORKER_SOCKET_PATH

if __name__ == "__main__":
    Remote(socket_path=WORKER_SOCKET_PATH % 2)
