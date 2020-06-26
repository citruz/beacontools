import sys

if sys.platform.startswith("linux"):
    from .bluez import *
else:
    raise NotImplementedError("Scanning not supported on this platform")
