from ja.common.message.base import Serializable


class Config(Serializable):
    """
    Base class for hierarchical configuration (files). The properties of Config
    objects are equivalent to the arguments of CLIs. Can override properties
    of other Config objects of the same type (or a subtype). Provides the
    option to only override unset properties.

    Command line arguments override user-specified configuration files.
    User-specified configuration files override global configuration files.
    """
