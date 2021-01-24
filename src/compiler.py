import ast
from validator import validate


class Parser(ast.NodeTransformer):
    def __init__(self, source_code):
        self.source_code = source_code
        self.parse_tree = None

    def parse(self):
        self.parse_tree = ast.parse(self.source_code)
        self.__iterate()
        return self.parse_tree

    def __iterate(self):
        children = self.visit(self.parse_tree).body

        for child in children:
            self.__visit(child)
        return True

    def __visit(self, node):
        validate(node)

        for field_name, value in ast.iter_fields(node):
            if isinstance(value, ast.AST):
                self.__visit(value)
