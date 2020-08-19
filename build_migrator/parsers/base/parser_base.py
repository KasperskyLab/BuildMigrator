from build_migrator.modules import Parser


class ParserBase(Parser):
    def __init__(self, context):
        self.context = context

    @staticmethod
    def is_applicable(project=None, log_type=None):
        return True

    def input_dir(self, state, dest, value):
        path = value[-1]
        dependencies = state.get_attribute("dependencies", [])
        path = self.context.get_dir_arg(self.context.normalize_path(path), dependencies)
        value[-1] = path
        state.set_attribute("dependencies", dependencies)
        state.append_or_extend_attribute(dest, value)

    def input_file(self, state, dest, value):
        path = value[-1]
        dependencies = state.get_attribute("dependencies", [])
        path = self.context.get_file_arg(
            self.context.normalize_path(path), dependencies
        )
        value[-1] = path
        state.set_attribute("dependencies", dependencies)
        state.append_or_extend_attribute(dest, value)

    def input_file_after_equals_sign(self, state, dest, value):
        flag, path = value[-1].split("=")
        dependencies = state.get_attribute("dependencies", [])
        path = self.context.get_file_arg(
            self.context.normalize_path(path), dependencies
        )
        value[-1] = flag + "=" + path
        state.set_attribute("dependencies", dependencies)
        state.append_or_extend_attribute(dest, value)

    def output_file(self, state, dest, value):
        path = value[-1]
        dependencies = state.get_attribute("dependencies", [])
        path = self.context.get_output(self.context.normalize_path(path), dependencies)
        value[-1] = path
        state.set_attribute("dependencies", dependencies)
        state.set_attribute("output", path)
        state.append_or_extend_attribute(dest, value)
