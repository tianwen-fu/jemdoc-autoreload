from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser


class Command(metaclass=ABCMeta):
    @abstractmethod
    def add_arguments(self, parser: ArgumentParser):
        pass

    @abstractmethod
    def run(self, args):
        pass
