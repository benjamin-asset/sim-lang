import ast
import exception


forbidden_function_list = ['open', 'id']


class NodeValidator(ast.NodeTransformer):
    def __init__(self, parse_tree):
        self.parse_tree = parse_tree

    def validate(self):
        children = self.visit(self.parse_tree).body

        for child in children:
            self.__validate(child)

    def __validate(self, node):
        # import 문 금지
        if isinstance(node, ast.Import):
            raise exception.TryImportClauseException(node.end_lineno)

        # with 문 금지
        if isinstance(node, ast.With):
            raise exception.TryWithClauseException(node.end_lineno)

        '''
        특정 함수 금지
        함수 호출이 아니라 Name 을 통한 함수 접근 자체를 막아야함
        예를 들어
        fakeOpen = open
        fakeOpen('sql.properties', 'w')
        이런식으로 호출 할 수도 있기 때문
        '''
        if isinstance(node, ast.Name) and node.id in forbidden_function_list:
            raise exception.CallForbiddenFunctionException(node.end_lineno, node.id)

        for field_name, value in ast.iter_fields(node):
            if isinstance(value, ast.AST):
                self.__validate(value)
