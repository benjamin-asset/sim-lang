import pandas as pd
import ast
import requests
import re

from docstring_parser import parse

indicator_url = "https://raw.githubusercontent.com/benjamin-asset/utils/master/utils/indicator.py"
function_url = "https://raw.githubusercontent.com/benjamin-asset/utils/master/utils/function.py"

# 변수 가능하게
# 빌트인 변수


def docs_to_parsed_data(docs, module_name: str):
    tree = ast.parse(docs)
    functions = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        docstring = ast.get_docstring(node)
        if docstring is None:
            continue

        parsed_docstring = parse(docstring)
        # print(docstring)
        params = []
        for param in parsed_docstring.params:
            if len(param.description) == 0:
                continue
            korean_name = re.search(r"(?<=\().+?(?=\))", param.description).group()
            params.append(Param(param.arg_name, korean_name))

        function_data = Function(
            node.name,
            parsed_docstring.short_description.replace(" ", ""),
            module_name,
            params
        )

        functions.append(function_data)
    return functions


class Component:
    def __init__(self, en_name: str, kr_name: str):
        self.en_name = en_name
        self.kr_name = kr_name

    def __eq__(self, other):
        if isinstance(other, str):
            return self.en_name == other or self.kr_name == other
        return False

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


class Param(Component):
    def __init__(self, en_name: str, kr_name: str):
        super().__init__(en_name, kr_name)

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


class Function(Component):
    def __init__(self, en_name: str, kr_name: str, module: str, param_list):
        super().__init__(en_name, kr_name)
        self.module = module
        self.param_list = param_list

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


class Field(Component):
    def __init__(self, en_name: str, kr_name: str):
        super().__init__(en_name, kr_name)


field_list = [
    Field('close', '종가'),
    Field('high', '고가'),
    Field('low', '저가'),
    Field('log', '정해야함!!!!!!!!!!!!'),
    Field('tr_val', '정해야함!!!!!!!!!!!!'),
]
forbidden_function_list = ['open', 'id']
forbidden_clause_list = [ast.Import, ast.With, ast.Return]
built_in_variable_list = ['df', 'result', 'usd', 'yen', 'euro']

built_in_function_list = []
indicator_text = requests.get(indicator_url).text
built_in_function_list.extend(
    docs_to_parsed_data(indicator_text, 'indicator')
)

function_text = requests.get(function_url).text
built_in_function_list.extend(
    docs_to_parsed_data(function_text, 'function')
)

built_in_function_list.append(
    Function('ts_delay', '정해야함', 'language', None)
)


def ts_delay(series: pd.Series, num: int):
    if num < 0:
        num *= -1
    return series.shift(num)
