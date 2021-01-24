class CompileError(Exception):
    def __init__(self, code, message, line_num, data=None):
        self.code = code
        self.message = message
        self.line_num = line_num
        self.data = data


class TryImportException(CompileError):
    def __init__(self, line_num):
        self.code = "CP-1"
        self.message = "import 문을 사용할 수 없습니다"
        self.line_num = line_num


