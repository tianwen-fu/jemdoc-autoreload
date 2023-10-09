from jemdoc_autoreload.commands import Command
from pathlib import Path
import multiprocessing as mp


class ServeCommand(Command):
    def add_arguments(self, parser):
        parser.add_argument("path", metavar="PATH", help="path to the project folder")

    def run(self, args):
        root_path = Path(args.path).resolve()
        src_path = root_path / "src"
        html_path = root_path / "html"
        static_path = root_path / "static"
        if not all(p.exists() for p in (root_path, src_path, html_path, static_path)):
            raise ValueError(f"{root_path} is not a valid jemdoc-autoreload project")

        # compile
