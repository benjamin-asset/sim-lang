class RuntimeException(Exception):
    def __init__(self, code, message, line_num, data=None):
        self.code = code
        self.message = message
        self.line_num = line_num
        self.data = data


class CompileError(Exception):
    def __init__(self, code, message, line_num, data=None):
        self.code = code
        self.message = message
        self.line_num = line_num
        self.data = data


class UseForbiddenClauseException(CompileError):
    def __init__(self, line_num, clause_name):
        super().__init__("CP-1", f"{clause_name} 문은 사용할 수 없습니다", line_num)


class CallForbiddenFunctionException(CompileError):
    def __init__(self, line_num, function_name):
        super().__init__("CP-2", f"{function_name} 함수는 사용할 수 없습니다", line_num)


class AccessBuiltInVariableException(CompileError):
    def __init__(self, line_num, variable_name):
        super().__init__("CP-3", f"{variable_name} 변수는 내장 변수이므로 사용할 수 없습니다", line_num)


class UnDefinedFieldException(CompileError):
    def __init__(self, line_num, field):
        super().__init__("CP-4", f"{field} 는 정의되지 않은 필드입니다.", line_num)
