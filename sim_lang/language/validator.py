import exception
from language import language_definition


def extract_clause_name(node):
    type_name = str(type(node))
    tmp = type_name[type_name.index("ast.") + 4 :]
    name = tmp[: tmp.index("'")]
    return name


def validate(node):
    if type(node) in language_definition.forbidden_clause_list:
        raise exception.UseForbiddenClauseException(node.end_lineno, extract_clause_name(node))
    return True


def validate_name(node):
    """
    특정 함수 금지
    함수 호출이 아니라 Name 을 통한 함수 접근 자체를 막아야함
    예를 들어
    fakeOpen = open
    fakeOpen('sql.properties', 'w')
    이런식으로 호출 할 수도 있기 때문
    """
    if node.id in language_definition.forbidden_function_list:
        raise exception.CallForbiddenFunctionException(node.end_lineno, node.id)

    if node.id in language_definition.built_in_variable_list:
        raise exception.AccessBuiltInVariableException(node.end_lineno, node.id)
    return True
