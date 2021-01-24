class CompileError(Exception):
    def __init__(self, code, message, line_num, data=None):
        self.code = code
        self.message = message
        self.line_num = line_num
        self.data = data


class UseForbiddenClauseException(CompileError):
    def __init__(self, line_num, clause_name):
        self.code = "CP-1"
        self.message = f"{clause_name} 문을 사용할 수 없습니다"
        self.line_num = line_num


class CallForbiddenFunctionException(CompileError):
    def __init__(self, line_num, function_name):
        self.code = "CP-2"
        self.message = f"{function_name} 함수는 사용할 수 없습니다"
        self.line_num = line_num

