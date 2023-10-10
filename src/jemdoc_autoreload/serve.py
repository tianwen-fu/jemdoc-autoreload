import os
import shutil
import subprocess as sp
import time
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from jemdoc_autoreload.commands import Command
from jemdoc_autoreload.jemdoc import main as compile_jemdoc


def compile(root_path, files_to_compile=None, *, clear_html=True, check_crlf=True):
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
        if os.name == "nt" and check_crlf:
            # convert CRLF to LF, since jemdoc does not support CRLF
            with open(src_file, "rb") as f:
                content = f.read()
            if b"\r\n" in content:
                with open(src_file, "wb") as f:
                    f.write(content.replace(b"\r\n", b"\n"))
                if not clear_html:
                    continue  # skip this file, since it will be recompiled anyway

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

    # copy static files
    if clear_html:
        for file in static_path.rglob("*"):
            if file.is_file():
                shutil.copyfile(file, html_path / file.relative_to(static_path))


class JemdocEventHandler(PatternMatchingEventHandler):
    def __init__(self, root_path, check_crlf):
        self.root_path = root_path
        self.html_path = root_path / "html"
        self.static_path = root_path / "static"
        self.check_crlf = check_crlf
        super().__init__(
            patterns=["src/*.jemdoc", "src/MENU", "mysite.conf", "static/*"],
            ignore_patterns=["*.html"],
            ignore_directories=False,
            case_sensitive=False,
        )

    def on_created(self, event):
        source = Path(event.src_path)
        if source.suffix == ".jemdoc":
            print(f"Compiling {source}...")
            compile(
                self.root_path,
                files_to_compile=[source],
                clear_html=False,
                check_crlf=self.check_crlf,
            )
        elif source.parent.name == "static":
            print(f"Copying {source}...")
            shutil.copyfile(
                source, self.html_path / source.relative_to(self.static_path)
            )
        elif source.name == "MENU":
            # recompile all
            print("Menu changed, recompiling all...")
            compile(self.root_path, clear_html=True, check_crlf=self.check_crlf)
        else:
            raise ValueError(f"Unknown file type: {source}")

    def on_modified(self, event):
        source = Path(event.src_path)
        if source.name == "mysite.conf":
            # recompile all
            print("Site config changed, recompiling all...")
            compile(self.root_path, clear_html=True, check_crlf=self.check_crlf)
        else:
            return self.on_created(event)

    def on_deleted(self, event):
        source = Path(event.src_path)
        if source.suffix == ".jemdoc":
            print(f"Deleting {source}...")
            html_file = self.html_path / source.relative_to(
                self.root_path / "src"
            ).with_suffix(".html")
            if html_file.exists():
                html_file.unlink()
        elif source.parent.name == "static":
            print(f"Deleting {source}...")
            html_file = self.html_path / source.relative_to(self.static_path)
            if html_file.exists():
                html_file.unlink()
        else:
            # don't care
            pass


class ServeCommand(Command):
    def add_arguments(self, parser):
        parser.add_argument("path", metavar="PATH", help="path to the project folder")
        parser.add_argument("--port", type=int, default=8000, help="port to serve on")
        parser.add_argument(
            "--no-crlf-check",
            action="store_false",
            dest="check_crlf",
            help="disable CRLF check",
        )

    def run(self, args):
        root_path = Path(args.path).resolve()
        # compile once
        print("Compiling")
        compile(root_path)

        # serve
        print("Serving")
        server_address = ("", args.port)
        httpd = HTTPServer(
            server_address,
            partial(SimpleHTTPRequestHandler, directory=root_path / "html"),
        )
        httpd.timeout = 0.5
        httpd_thread = Thread(target=httpd.serve_forever, args=(0.5,))
        observer = Observer()
        observer.schedule(
            JemdocEventHandler(root_path, check_crlf=args.check_crlf),
            root_path,
            recursive=True,
        )
        try:
            httpd_thread.start()
            observer.start()
            while True:
                time.sleep(1)
                if not httpd_thread.is_alive():
                    raise RuntimeError("HTTP server thread died")
                if not observer.is_alive():
                    raise RuntimeError("Observer thread died")
        except KeyboardInterrupt:
            print("Keyboard interrupt detected, leaving...")
        finally:
            print("Shutting down threads...")
            httpd.shutdown()
            httpd_thread.join()
            observer.stop()
            observer.join()
