from build_migrator.modules import EntryPoint, Builder


class Ext1(Builder, EntryPoint):
    @staticmethod
    def add_arguments(argument_parser):
        argument_parser.add_argument('--myarg', required=True)

    def __init__(self, myarg):
        self._myarg = myarg

    def build(self, builders):
        pass


__all__ = ['Ext1']
