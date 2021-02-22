import unittest

import exception
from language.compiler import Compiler


class MyTestCase(unittest.TestCase):
    def testBlockImport(self):
        compiler = Compiler(
            """
import ast
            """
        )
        self.assertRaises(exception.UseForbiddenClauseException, lambda: compiler.compile())

    def testBlockImport2(self):
        compiler = Compiler(
            """
1+2
import ast
            """
        )
        self.assertRaises(exception.UseForbiddenClauseException, lambda: compiler.compile())

    def testBlockWith(self):
        compiler = Compiler(
            """
with open('hi.txt', 'f'):
    pass
            """
        )
        self.assertRaises(exception.UseForbiddenClauseException, lambda: compiler.compile())

    def testBlockOpen(self):
        compiler = Compiler(
            """
a = open
            """
        )
        self.assertRaises(exception.CallForbiddenFunctionException, lambda: compiler.compile())

    def testBlockOpen2(self):
        compiler = Compiler(
            """
a = open('file', 'r')
            """
        )
        self.assertRaises(exception.CallForbiddenFunctionException, lambda: compiler.compile())

    def testBlockId(self):
        compiler = Compiler(
            """
a = id(open)
            """
        )
        self.assertRaises(exception.CallForbiddenFunctionException, lambda: compiler.compile())


if __name__ == '__main__':
    unittest.main()
