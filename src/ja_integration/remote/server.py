from ja.common.proxy.remote import Remote
from ja_integration.remote import SERVER_SOCKET_PATH

if __name__ == "__main__":
    Remote(socket_path=SERVER_SOCKET_PATH)
