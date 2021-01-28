from exception import CompileError, RuntimeException


def handle_compile_error(exception: CompileError):
    print(exception.code)
    print(exception.message)
    print(exception.line_num)
    if exception.data is not None:
        print(exception.data)


def handle_runtime_error(exception):
    print(exception.code)
    print(exception.message)
    print(exception.line_num)
    if exception.data is not None:
        print(exception.data)
