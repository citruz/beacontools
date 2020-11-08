"""Load a different backend depending on the OS."""
import sys

if sys.platform.startswith("linux"):
    from .linux import *
elif sys.platform.startswith("freebsd"):
    from .freebsd import *
else:
    raise NotImplementedError("Scanning not supported on this platform")
