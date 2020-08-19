from build_migrator.modules import Builder


class Ext2(Builder):
    priority = 1

    def __call__(self, context):
        pass


__all__ = ['Ext2']
