from argparse import ArgumentParser
from jemdoc_autoreload import COMMANDS


def parse_args():
    parser = ArgumentParser(
        prog="jemdoc-autoreload", description="a simple jemdoc autoreload server"
    )
    subparsers = parser.add_subparsers(
        title="command",
        dest="command",
        help="command to run",
        required=True,
        metavar="COMMAND",
    )
    for name, command in COMMANDS.items():
        command_instance = command()
        command_parser = subparsers.add_parser(name, help=command_instance.__doc__)
        command_instance.add_arguments(command_parser)
    return parser.parse_args()


def main():
    args = parse_args()
    command = COMMANDS[args.command]()
    command.run(args)


if __name__ == "__main__":
    main()
