import sys

if sys.platform.startswith("linux"):
    from .bluez import *
elif sys.platform.startswith("freebsd"):
    from .freebsd import *
else:
    raise NotImplementedError("Scanning not supported on this platform")
