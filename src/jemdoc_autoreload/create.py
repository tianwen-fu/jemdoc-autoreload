from jemdoc_autoreload.commands import Command
from pathlib import Path
from importlib_resources import files
import shutil


class CreateCommand(Command):
    def add_arguments(self, parser):
        parser.add_argument("path", metavar="PATH", help="path to create project in")

    def run(self, args):
        path = Path(args.path).resolve()
        if path.exists():
            raise ValueError(f"{path} already exists")
        for subpath in ("html", "src", "static"):
            (path / subpath).mkdir(parents=True)

        # copy asset files
        shutil.copyfile(
            files("jemdoc_autoreload_assets").joinpath("jemdoc.css"),
            path / "static" / "jemdoc.css",
        )
        shutil.copyfile(
            files("jemdoc_autoreload_assets").joinpath("mysite.conf"),
            path / "mysite.conf",
        )
        shutil.copyfile(
            files("jemdoc_autoreload_assets").joinpath("MENU"),
            path / "src" / "MENU",
        )

        with open(path / ".gitignore", "w") as f:
            print("html/", file=f)

        with open(path / "src" / "index.jemdoc", "w") as f:
            print("# jemdoc: menu{MENU}{mathjax.html}, nofooter\n== Title", file=f)
