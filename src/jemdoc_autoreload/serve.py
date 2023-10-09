from jemdoc_autoreload.commands import Command
from pathlib import Path
import subprocess as sp
from jemdoc_autoreload.jemdoc import main as compile_jemdoc


def compile(root_path, files_to_compile=None, clear_html=True):
    src_path = root_path / "src"
    html_path = root_path / "html"
    static_path = root_path / "static"
    if not all(p.exists() for p in (root_path, src_path, html_path, static_path)):
        raise ValueError(f"{root_path} is not a valid jemdoc-autoreload project")

    if clear_html:
        for file in html_path.rglob("*"):
            if file.is_file():
                file.unlink()

    # compile
    if files_to_compile is None:
        files_to_compile = src_path.rglob("*.jemdoc")
    for src_file in files_to_compile:
        html_file = html_path / src_file.relative_to(src_path).with_suffix(".html")
        # ! known bug: to my best knowledge, jemdoc does not have a config for "site root"
        # ! therefore, it is most likely that the compiled html files won't render properly
        # ! since the relative paths to the static files (e.g. CSS) will be wrong
        html_file.parent.mkdir(parents=True, exist_ok=True)
        jemdoc_args = [
            "jemdoc",  # a dummy arg to fill in the 0th arg
            "-o",
            str(html_file),
            "-c",
            str(root_path / "mysite.conf"),
            str(src_file),
        ]
        compile_jemdoc(jemdoc_args)


class ServeCommand(Command):
    def add_arguments(self, parser):
        parser.add_argument("path", metavar="PATH", help="path to the project folder")

    def run(self, args):
        root_path = Path(args.path).resolve()
        # compile once
        print("Compiling")
        compile(root_path)

        # then, ask watchdog to recompile when files change
