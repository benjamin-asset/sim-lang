import ast
from utils.function import Function
from utils.indicator import Indicator
from typing import Any
import pandas as pd
import exception
import language_definition

from validator import validate, validate_name


class Compiler(ast.NodeTransformer):
    def __init__(self, source_code):
        self.source_code = source_code
        self.expression_tree = None

    class Name(ast.Name):
        def __init__(self, identifier_id, expr_context_ctx=ast.Load()):
            super().__init__(identifier_id, expr_context_ctx)
            ast.Name.__setattr__(self, 'id', identifier_id)

    class Attribute(ast.Attribute):
        def __init__(self, expr_value, identifier_attr, expr_context_ctx=ast.Load()):
            super().__init__(expr_value, identifier_attr, expr_context_ctx)
            ast.Attribute.__setattr__(self, 'attr', identifier_attr)
            ast.Attribute.__setattr__(self, 'value', expr_value)

    def visit_Name(self, node: Name) -> Any:
        validate_name(node)
        return node

    def visit_Call(self, node: ast.Call) -> Any:
        function_name = None
        if isinstance(node.func, ast.Attribute):
            function_name = node.func.value.id
        elif isinstance(node.func, ast.Name):
            function_name = node.func.id

        if function_name == 'sma':
            clazz = ast.copy_location(self.Name('Indicator'), node)
            function = ast.copy_location(self.Attribute(clazz, 'get_sma'), node)

            args = list()
            for argument in node.args:
                if isinstance(argument.value, str):
                    if argument.value not in language_definition.field_list:
                        raise exception.UnDefinedFieldException(node.end_lineno, argument.value)

                    # 문자열 파라미터는 Series 참조로 변환
                    # 예) 'close' -> df['close']
                    sub = ast.Subscript(
                        ast.Name(
                            'df',
                            ast.Load()
                        ),
                        argument,
                        ast.Load()
                    )
                    args.append(sub)

                if isinstance(argument.value, int):
                    # 정수형 파라미터는 그대로 전달
                    args.append(argument)

            return ast.copy_location(
                ast.Call(
                    expr_func=function,
                    expr=function,
                    func=function,
                    args=args,
                    keywords=[]
                ),
                node
            )

        return node

    def compile(self):
        self.expression_tree = ast.parse(self.source_code)
        print(ast.dump(self.expression_tree))
        self.__iterate()
        return self.expression_tree

    def __iterate(self):
        children = self.visit(self.expression_tree).body

        for child in children:
            self.__visit(child)
        return True

    def __visit(self, node):
        validate(node)

        for field_name, value in ast.iter_fields(node):
            if isinstance(value, ast.AST):
                self.__visit(value)
