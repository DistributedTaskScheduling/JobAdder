from typing import Callable, Any


def skipIfAbstract(f: Callable[..., None]) -> Callable[..., None]:
    def wrapper(*args: Any) -> None:
        self = args[0]
        if "Abstract" not in type(args[0]).__name__:
            f(*args)
        else:
            self.skipTest('Test is in abstract base class')
    return wrapper
