import ast


field_list = ['close']
forbidden_function_list = ['open', 'id']
forbidden_clause_list = [ast.Import, ast.With, ast.Return]
built_in_variable_list = ['df', 'result']
