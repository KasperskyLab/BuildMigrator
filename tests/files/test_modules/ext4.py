from build_migrator.modules import EntryPoint, Builder


class Ext4(EntryPoint, Builder):
    def __init__(self, myarg):
        self._myarg = myarg

    def build(self, builders):
        pass


__all__ = ['Ext4']
