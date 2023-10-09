from jemdoc_autoreload.create import CreateCommand
from jemdoc_autoreload.serve import ServeCommand

__all__ = ["__version__", "COMMANDS"]

COMMANDS = dict(create=CreateCommand, serve=ServeCommand)
__version__ = "0.1.0"
