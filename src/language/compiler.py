import io
import time
import logging

from collections import deque
from typing import Any
from anytree import Node, PostOrderIter

from exception import *
from language.language_definition import *
from language.constant import RESULT_COLUMN, PRIORITY_COLUMN, BUY_PRICE_COLUMN, SELL_PRICE_COLUMN
from utils.parameter import Field
import inspect
import utils.indicator
import enum
from language.language_utils import import_module

indicator = import_module('utils', 'indicator')
function = import_module('utils', 'function')
language = import_module('language', 'language_definition')
parameter = import_module('utils', 'parameter')


class CompileResult:
    class Item:
        def __init__(self, code: str, is_rank: bool):
            self.code = code
            self.is_rank = is_rank

    def __init__(self, item_list: list, fields: set, max_ts_delay: int, priority):
        self.item_list = item_list
        self.fields = fields
        self.max_ts_delay = max_ts_delay
        self.priority = priority


class Name(ast.Name):
    def __init__(self, identifier_id, expr_context_ctx=ast.Load()):
        super().__init__(identifier_id, expr_context_ctx)
        ast.Name.__setattr__(self, 'id', identifier_id)


class Attribute(ast.Attribute):
    def __init__(self, value, attr, expr_context_ctx=ast.Load()):
        super().__init__(value, attr, expr_context_ctx)
        ast.Attribute.__setattr__(self, 'attr', attr)
        ast.Attribute.__setattr__(self, 'value', value)


class Call(ast.Call):
    def __init__(self, function, arguments):
        super().__init__(
            expr_func=function,
            expr=function,
            func=function,
            args=arguments,
            keywords=[]
        )
        self.name = call_to_name(self)


class InnerFunction:
    def __init__(self, node: ast.Call, is_rank: bool):
        self.node = node
        self.name = call_to_name(node)
        self.is_rank = is_rank

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return self.name.__hash__()

    def __lt__(self, other):
        return self.name < other.name


class Compiler(ast.NodeTransformer):
    def __init__(self):
        self.reset()

    def reset(self):
        self.function_dependency_tree = Node("root")
        self.function_dependency_stack = deque()
        self.function_dependency_stack.appendleft(self.function_dependency_tree)
        self.functions = dict()
        self.expression_stack = deque()
        self.expression_ast_tree = None
        self.rank_function_list = list()
        self.fields = set()
        self.max_ts_delay = 0

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

    def visit_Name(self, node: Name) -> Any:
        arg = ast.Constant(node.id, node.id)
        return to_field(arg)

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        return node

    def visit_BoolOp(self, node: ast.BoolOp) -> Any:
        if isinstance(node.op, ast.And):
            fun = to_and
        elif isinstance(node.op, ast.Or):
            fun = to_or
        else:
            raise Exception()

        while len(node.values) > 2:
            last = node.values.pop(0)
            prev = node.values.pop(0)
            new_node = fun(self.visit(last), self.visit(prev))
            node.values.insert(0, new_node)
        return fun(self.visit(node.values[0]), self.visit(node.values[1]))

    def visit_If(self, node: ast.If) -> Any:
        if len(node.orelse) == 0:
            raise ElseIsNotDefinedException(node.end_lineno)

        item = node.body[0]
        else_item = node.orelse[0]

        test = self.visit(node.test)
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
                    self.visit(else_item.value)
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
                        to_and(value, self.visit(item.value)),
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

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        if isinstance(node.op, ast.Div):
            return ast.copy_location(
                ast.BinOp(
                    self.visit(node.left),
                    ast.Div(),
                    Call(
                        Attribute(Name('df'), 'where'),
                        [
                            ast.Compare(
                                left=self.visit(node.right),
                                ops=[ast.NotEq()],
                                comparators=[ast.Constant(0, 0)]
                            ),
                            ast.Constant(1e-8, 1e-8)
                        ]
                    )
                ), node
            )
        return node

    def visit_Call(self, node: ast.Call) -> Any:
        function_name = None
        if isinstance(node.func, ast.Attribute):
            function_name = node.func.value.id
        elif isinstance(node.func, ast.Name):
            function_name = node.func.id

        is_rank = False
        # 랭크함수가 있는지 확인
        if function_name == 'rank':
            is_rank = True

        parent_dependency_node = Node(function_name, self.function_dependency_stack[0])
        self.function_dependency_stack.appendleft(parent_dependency_node)

        if function_name in built_in_function_list:
            fun = built_in_function_list[built_in_function_list.index(function_name)]
            args = list()
            callable_function = None
            if fun.module == 'language':
                callable_function = getattr(language, function_name)
            elif fun.module == 'indicator':
                callable_function = getattr(indicator, function_name)
            elif fun.module == 'function':
                callable_function = getattr(function, function_name)
            else:
                raise Exception()

            function_spec = inspect.getfullargspec(callable_function)
            function_parameter_name_list = function_spec[0]
            function_annotation_list = function_spec.annotations

            for index, argument in enumerate(node.args):
                parameter_name = function_parameter_name_list[index]
                parameter_type = function_annotation_list[parameter_name]
                is_enum = isinstance(parameter_type, enum.EnumMeta)
                if is_enum:
                    enum_node = ast.copy_location(
                        Attribute(Attribute(Name("parameter"), get_enum_name(parameter_type)), argument.id),
                        argument
                    )
                    args.append(enum_node)

                elif isinstance(argument, ast.Name):
                    if argument.id in Field.__members__:
                        self.fields.add(Field.__members__[argument.id])
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

            if fun.en_name == 'ts_delay' and self.max_ts_delay < node.args[1].value:
                self.max_ts_delay = node.args[1].value
            node = make_function_call(fun.module, fun.en_name, args, node)
        else:
            pass

        self.function_dependency_stack.popleft()
        inner_function = InnerFunction(node, is_rank)
        parent_dependency_node.name = inner_function.name
        self.functions[inner_function.name] = inner_function
        return to_field(make_constant(inner_function.name))

    def compile(self, source_code: str, priority_code: str, buy_price_code: str, sell_price_code: str) -> CompileResult:
        now = time.time()
        self.reset()
        source_code = remove_indent(source_code)
        priority_code = remove_indent(priority_code)
        buy_price_code = remove_indent(buy_price_code)
        sell_price_code = remove_indent(sell_price_code)

        expression_tree = ast.parse(source_code)
        priority_expression_tree = ast.parse(priority_code)
        buy_price_expression_tree = ast.parse(buy_price_code)
        sell_price_expression_tree = ast.parse(sell_price_code)

        self.visit(expression_tree)
        self.visit(priority_expression_tree)
        self.visit(buy_price_expression_tree)
        self.visit(sell_price_expression_tree)

        result_item_list = list()

        # 사용된 함수, 파라미터 쌍을 코드로 변환함. 미리 필드로 정의해두고, 참조만 하기 위해서
        added_function_set = set()
        body = list()
        cur_is_rank = False
        for index, node in enumerate(PostOrderIter(self.function_dependency_tree)):
            if node.name == 'root':
                if len(body) > 0:
                    function_tree = ast.Module(
                        body=body,
                        type_ignores=[]
                    )
                    function_code = ast.unparse(function_tree)
                    result_item_list.append(CompileResult.Item(function_code, cur_is_rank))
                break

            function = self.functions[node.name]
            if function.is_rank != cur_is_rank:
                if len(body) > 0:
                    function_tree = ast.Module(
                        body=body,
                        type_ignores=[]
                    )
                    function_code = ast.unparse(function_tree)
                    result_item_list.append(CompileResult.Item(function_code, cur_is_rank))
                    body = list()

            cur_is_rank = function.is_rank

            if function.name in added_function_set:
                continue

            added_function_set.add(function.name)
            body.append(
                ast.Assign(
                    targets=[to_field(make_constant(node.name))],
                    value=function.node,
                    lineno=index
                )
            )

        expression_code = f"df['{RESULT_COLUMN}'] = df['is_active'] & ({ast.unparse(expression_tree)})"
        result_item_list.append(CompileResult.Item(expression_code, False))

        priority_expression_code = f"df['{PRIORITY_COLUMN}'] = {ast.unparse(priority_expression_tree)}"
        result_item_list.append(CompileResult.Item(priority_expression_code, False))

        priority_expression_code = f"df['{BUY_PRICE_COLUMN}'] = {ast.unparse(buy_price_expression_tree)}"
        result_item_list.append(CompileResult.Item(priority_expression_code, False))

        priority_expression_code = f"df['{SELL_PRICE_COLUMN}'] = {ast.unparse(sell_price_expression_tree)}"
        result_item_list.append(CompileResult.Item(priority_expression_code, False))

        logging.debug('[Profiler] Compile time : {:0.3f}s'.format(time.time() - now))
        return CompileResult(result_item_list, self.fields, self.max_ts_delay, priority_expression_code)


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
        elif isinstance(arg, ast.Attribute):
            args.append(arg.attr)
        else:
            args.append(str(arg))

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


def get_enum_name(enum_meta: enum.EnumMeta) -> str:
    return str(enum_meta)[str(enum_meta).index("'") + 1: str(enum_meta).rindex("'")]
