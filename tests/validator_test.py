import unittest

import exception
from parser import Parser


class MyTestCase(unittest.TestCase):
    def testBlockImport(self):
        parser = Parser(
            """
import ast
            """
        )
        self.assertRaises(exception.UseForbiddenClauseException, lambda: parser.parse())

    def testBlockImport2(self):
        parser = Parser(
            """
1+2
import ast
            """
        )
        self.assertRaises(exception.UseForbiddenClauseException, lambda: parser.parse())

    def testBlockWith(self):
        parser = Parser(
            """
with open('hi.txt', 'f'):
    pass
            """
        )
        self.assertRaises(exception.UseForbiddenClauseException, lambda: parser.parse())

    def testBlockOpen(self):
        parser = Parser(
            """
a = open
            """
        )
        self.assertRaises(exception.CallForbiddenFunctionException, lambda: parser.parse())

    def testBlockOpen2(self):
        parser = Parser(
            """
a = open('file', 'r')
            """
        )
        self.assertRaises(exception.CallForbiddenFunctionException, lambda: parser.parse())

    def testBlockId(self):
        parser = Parser(
            """
a = id(open)
            """
        )
        self.assertRaises(exception.CallForbiddenFunctionException, lambda: parser.parse())


if __name__ == '__main__':
    unittest.main()
