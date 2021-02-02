from compiler import Compiler, remove_indent, normalize
from language_utils import import_class

Indicator = import_class('utils', 'Indicator')
Function = import_class('utils', 'function', 'Function')

import executor

compiler = Compiler()


# def test_execute():
#     compiled_code = compiler.compile(
#         """
#         if momentum(close, 60) >= 0.1:
#             if momentum(close, 60) >= 0.2:
#                 (sma(close, 21) <= 0.3)
#             else:
#                 (sma(close, 21) <= 0.4)
#         else:
#             (sma(close, 21) <= 0.5)
#         """
#     )
#     assert True


def test_execute2():
    compiled_code = compiler.compile(
        """
        (sma(close, 21) <= 0.3)
        """
    )
    target_code = normalize(
        remove_indent(
            """
            df['#Indicator_get_sma_close_21'] = Indicator.get_sma(df['close'], 21)
            results['result'] = df['#Indicator_get_sma_close_21'] <= 0.3
            """
        )
    )
    assert (compiled_code == target_code)
