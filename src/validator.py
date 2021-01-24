import ast
import exception


class NodeValidator(ast.NodeTransformer):
    def __init__(self, parse_tree):
        self.parse_tree = parse_tree

    def validate(self):
        children = self.visit(self.parse_tree).body

        for child in children:
            self.__validate(child)

    def __validate(self, node):
        if isinstance(node, ast.Import):
            raise exception.TryImportException(node.end_lineno)

        for field_name, value in ast.iter_fields(node):
            if isinstance(value, ast.AST):
                self.__validate(value)



