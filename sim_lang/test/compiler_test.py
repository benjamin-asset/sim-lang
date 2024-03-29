from language.compiler import Compiler, remove_indent, normalize
from language.language_utils import import_module

indicator = import_module("utils", "indicator")
function = import_module("utils", "function")
language = import_module("language", "language_definition")

compiler = Compiler()


# def test_execute():
#     compiled_code = compiler.language(
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


def test_simplest_code():
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
    assert compiled_code == target_code


def test_if():
    compiled_code = compiler.compile(
        """
        if sma(close, 22) <= 0.2:
            sma(close, 23) <= 0.3
        else:
            sma(close, 24) <= 0.4
        """
    )
    target_code = normalize(
        remove_indent(
            """
            df['#Indicator_get_sma_close_22'] = Indicator.get_sma(df['close'], 22)
            df['#Indicator_get_sma_close_23'] = Indicator.get_sma(df['close'], 23)
            df['#Indicator_get_sma_close_24'] = Indicator.get_sma(df['close'], 24)
            results['result'] = (df['#Indicator_get_sma_close_22'] <= 0.2) & (df['#Indicator_get_sma_close_23'] <= 0.3) | ~(df['#Indicator_get_sma_close_22'] <= 0.2) & (df['#Indicator_get_sma_close_24'] <= 0.4)
            """
        )
    )
    print(compiled_code)
    print(target_code)
    assert compiled_code == target_code


def test_divide():
    compile_result = compiler.compile(
        """
        (close / open) < 0.2
        """,
        """""",
        """""",
        """""",
    )
    target_code = normalize(
        remove_indent(
            """
            df['#result'] = df['is_active'] & (df['close'] / df.where(df['open'] != 0, 1e-8) < 0.2)
            """
        )
    )

    print(compile_result.item_list[-4].code)
    print(target_code)
    assert compile_result.item_list[-4].code == target_code
