class SSHConnection:
    """
    Establishes an SSH connection to a remote component. Writes Command objects
    the stdin of Remote objects. Then reads a Response object from stdout of
    the Remote object. Message objects are read/written as YAML strings.
    """
