import ast

# 변수 가능하게
# 빌트인 변수


class Function:
    def __init__(self, user_function: str, module: str, name: str):
        self.user_function = user_function
        self.module = module
        self.name = name

    def __eq__(self, other):
        if isinstance(other, str):
            return self.user_function == other
        return False


field_list = ['close', 'high', 'log']
forbidden_function_list = ['open', 'id']
forbidden_clause_list = [ast.Import, ast.With, ast.Return]
built_in_variable_list = ['df', 'result']

built_in_function_list = [
    Function('sma', 'Indicator', 'get_sma'),
    Function('momentum', 'Indicator', 'get_momentum'),
    Function('ibs', 'Indicator', 'get_ibs'),
    Function('envelope', 'Indicator', 'get_envelope'),
]
