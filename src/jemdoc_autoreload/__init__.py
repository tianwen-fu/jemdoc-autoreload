from jemdoc_autoreload.create import CreateCommand

__all__ = ["__version__", "COMMANDS"]

COMMANDS = dict(create=CreateCommand)
__version__ = "0.1.0"
