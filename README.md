# Jemdoc-autoreload

This is a simple script to automatically detect file changes, and recompile it when changed. It is based on the [jemdoc](http://jemdoc.jaboc.net/) project and [jemdoc+MathJax](http://web.stanford.edu/~wsshin/jemdoc+mathjax.html) modification. File changes are monitored by [watchdog](https://pypi.org/project/watchdog/).

It also creates a folder structure for management, starts a local HTTP server to preview the change, and converts CRLF to LF automatically on Windows systems.

## Usage
### Installation
By pip:
```bash
pip install git+https://github.com/tianwen-fu/jemdoc-autoreload.git
```

### Create a new project
```bash
python -m jemdoc_autoreload create <path_to_project>
```

### Start the server
```bash
python -m jemdoc_autoreload serve <path_to_project> --port <port_number>
```