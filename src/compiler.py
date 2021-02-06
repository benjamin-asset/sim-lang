import io
from collections import deque
from typing import Any
from anytree import Node, PostOrderIter

from exception import *
from language_definition import *
from language_utils import import_class


Indicator = import_class('utils', 'Indicator')
Function = import_class('utils', 'function', 'Function')


class CompileResult:
    def __init__(self, code: str, rank_function_list: list):
        self.code = code
        self.rank_function_list = rank_function_list


class Name(ast.Name):
    def __init__(self, identifier_id, expr_context_ctx=ast.Load()):
        super().__init__(identifier_id, expr_context_ctx)
        ast.Name.__setattr__(self, 'id', identifier_id)


class Attribute(ast.Attribute):
    def __init__(self, expr_value, identifier_attr, expr_context_ctx=ast.Load()):
        super().__init__(expr_value, identifier_attr, expr_context_ctx)
        ast.Attribute.__setattr__(self, 'attr', identifier_attr)
        ast.Attribute.__setattr__(self, 'value', expr_value)


class Call(ast.Call):
    def __init__(self, expr_func, expr, *args, **kwargs):
        super().__init__(expr_func, expr, *args, **kwargs)
        self.name = call_to_name(self)


class InnerFunction:
    def __init__(self, node: ast.Call):
        self.node = node
        self.name = call_to_name(node)

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return self.name.__hash__()

    def __lt__(self, other):
        return self.name < other.name


class Compiler(ast.NodeTransformer):
    def __init__(self):
        self.function_dependency_tree = Node("root")
        self.function_dependency_stack = deque()
        self.function_dependency_stack.appendleft(self.function_dependency_tree)
        self.functions = dict()
        self.expression_stack = deque()
        self.expression_ast_tree = None
        self.rank_function_list = list()

    def reset(self):
        self.function_dependency_tree = Node("root")
        self.function_dependency_stack = deque()
        self.function_dependency_stack.appendleft(self.function_dependency_tree)
        self.functions = dict()
        self.expression_stack = deque()
        self.expression_ast_tree = None
        self.rank_function_list = list()

    def get_bool_op(self, node, index=0):
        if len(self.expression_stack) == 0:
            return None

        if len(self.expression_stack) == 1:
            return self.expression_stack[0]

        if index + 2 == len(self.expression_stack):
            return ast.copy_location(
                to_and(self.expression_stack[index], self.expression_stack[index + 1]),
                node
            )

        return ast.copy_location(
            to_and(self.expression_stack[index], self.get_bool_op(node, index + 1)),
            node
        )

    def visit_If(self, node: ast.If) -> Any:
        if len(node.orelse) == 0:
            raise ElseIsNotDefinedException(node.end_lineno)

        item = node.body[0]
        else_item = node.orelse[0]

        test = self.generic_visit(node.test)
        not_test = to_not(test)

        if isinstance(else_item, ast.If):
            self.expression_stack.appendleft(not_test)
            else_result = self.visit_If(else_item)
            self.expression_stack.popleft()
        else:
            function_stack_data = self.get_bool_op(node)
            if function_stack_data is None:
                value = not_test
            else:
                value = to_and(function_stack_data, not_test)
            else_result = ast.copy_location(
                to_and(
                    value,
                    self.generic_visit(else_item.value)
                ),
                node
            )

        if isinstance(item, ast.Expr):
            function_stack_data = self.get_bool_op(node)
            if function_stack_data is None:
                value = test
            else:
                value = to_and(function_stack_data, test)
            node = ast.copy_location(
                to_or(
                    ast.copy_location(
                        to_and(value, self.generic_visit(item.value)),
                        node
                    ),
                    else_result
                ),
                node
            )

        elif isinstance(item, ast.If):
            self.expression_stack.appendleft(test)
            result = self.visit_If(item)
            self.expression_stack.popleft()

            node = ast.copy_location(
                to_or(result, else_result),
                node
            )

        else:
            raise Exception()

        return node

    def visit_Call(self, node: ast.Call) -> Any:
        function_name = None
        if isinstance(node.func, ast.Attribute):
            function_name = node.func.value.id
        elif isinstance(node.func, ast.Name):
            function_name = node.func.id

        # 랭크함수가 있는지 확인
        if function_name == 'rank':
            # TODO:
            self.has_rank_function = True

        parent_dependency_node = Node(function_name, self.function_dependency_stack[0])
        self.function_dependency_stack.appendleft(parent_dependency_node)

        if function_name in built_in_function_list:
            fun = built_in_function_list[built_in_function_list.index(function_name)]
            args = list()
            for argument in node.args:
                if isinstance(argument, ast.Name):
                    if argument.id in field_list:
                        arg = ast.Constant(argument.id, argument.id)

                    else:
                        raise UnDefinedFieldException(node.end_lineno, argument.id)

                    # Series 참조로 변환
                    # 예) close -> df['close']
                    args.append(to_field(arg))

                elif isinstance(argument, ast.Constant) and isinstance(argument.value, int):
                    # 정수형 파라미터는 그대로 전달
                    args.append(argument)

                elif isinstance(argument, ast.Call):
                    args.append(self.visit_Call(argument))

            node = make_function_call(fun.module, fun.name, args, node)
        else:
            pass

        self.function_dependency_stack.popleft()
        inner_function = InnerFunction(node)
        parent_dependency_node.name = inner_function.name
        self.functions[inner_function.name] = inner_function.node
        return to_field(make_constant(inner_function.name))

    def compile(self, source_code) -> CompileResult:
        self.reset()
        source_code = remove_indent(source_code)
        expression_tree = ast.parse(source_code)
        self.generic_visit(expression_tree)

        # 사용된 함수, 파라미터 쌍을 코드로 변환함. 미리 필드로 정의해두고, 참조만 하기 위해서
        body = list()
        for index, node in enumerate(PostOrderIter(self.function_dependency_tree)):
            if node.name == 'root':
                break

            body.append(
                ast.Assign(
                    targets=[to_field(make_constant(node.name))],
                    value=self.functions[node.name],
                    lineno=index
                )
            )

        function_tree = ast.Module(
            body=body,
            type_ignores=[]
        )

        function_code = ast.unparse(function_tree)
        expression_code = f"results['result'] = {ast.unparse(expression_tree)}"
        code = f'{function_code}\n{expression_code}'
        return CompileResult(normalize(code), self.rank_function_list)


def normalize(code):
    return ast.unparse(ast.parse(code))


def remove_indent(source_code):
    indent = 0
    count = 0
    indent_type = 0
    for c in source_code:
        if c == '\n':
            continue
        elif c == ' ':
            count += 1
            if count == 4:
                indent += 1
                count = 0
        elif c == '\t':
            indent_type = 1
            indent += 1
        else:
            break

    if indent > 0:
        buf = io.StringIO(source_code)
        lines = buf.readlines()
        source_code = ''
        if indent_type == 0:
            indent = indent * 4

        for line in lines:
            if len(line) <= indent:
                continue

            source_code += line[indent:]
    return source_code


def to_field(variable: ast.Constant, ctx=ast.Load()):
    return ast.Subscript(
        ast.Name(
            'df',
            ast.Load()
        ),
        variable,
        ctx
    )


def make_function_call(module_name: str, function_name: str, arguments: [ast.AST], node: ast.Call):
    clazz = ast.copy_location(Name(module_name), node)
    function = ast.copy_location(Attribute(clazz, function_name), node)
    return ast.copy_location(
        ast.Call(
            expr_func=function,
            expr=function,
            func=function,
            args=arguments,
            keywords=[]
        ),
        node
    )


def make_constant(value):
    return ast.Constant(value, value)


def call_to_name(node: ast.Call):
    args = list()
    for arg in node.args:
        if isinstance(arg, ast.Subscript):
            args.append(arg.slice.value)
        elif isinstance(arg, ast.Call):
            args.append(call_to_name(arg))
        elif isinstance(arg, ast.Name):
            args.append(arg.id)
        else:
            args.append(str(arg.value))

    if isinstance(node.func, ast.Attribute):
        function_id = f'{node.func.value.id}_{node.func.attr}'
    else:
        function_id = node.func.id
    return f'#{function_id}_{"_".join(args)}'


def to_not(test):
    return ast.UnaryOp(
        ast.Invert(),
        test
    )


def to_and(left, right):
    return ast.BinOp(
        left,
        ast.BitAnd(),
        right
    )


def to_or(left, right):
    return ast.BinOp(
        left,
        ast.BitOr(),
        right
    )
