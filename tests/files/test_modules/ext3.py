from build_migrator.modules import Builder
from .ext2 import Ext2


class Ext3a(Builder):
    priority = 5

    def __call__(self, context):
        pass

class Ext3b(Builder):
    priority = 6

    def __call__(self, context):
        pass


__all__ = ['Ext3a', 'Ext3b', 'Ext2']
