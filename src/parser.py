import ast


class Parser:
    def __init__(self, source_code):
        self.source_code = source_code
        self.parse_tree = self.parse()

    def parse(self):
        self.parse_tree = ast.parse(self.source_code)
        return self.parse_tree
