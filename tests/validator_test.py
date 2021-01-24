import unittest

import exception
from parser import Parser
from validator import NodeValidator


class MyTestCase(unittest.TestCase):
    def testBlockImport(self):
        parser = Parser(
            """
import ast
            """
        )
        validator = NodeValidator(parser.parse_tree)
        self.assertRaises(exception.UseForbiddenClauseException, lambda: validator.validate())

    def testBlockImport2(self):
        parser = Parser(
            """
1+2
import ast
            """
        )
        validator = NodeValidator(parser.parse_tree)
        self.assertRaises(exception.UseForbiddenClauseException, lambda: validator.validate())

    def testBlockWith(self):
        parser = Parser(
            """
with open('hi.txt', 'f'):
    pass
            """
        )
        validator = NodeValidator(parser.parse_tree)
        self.assertRaises(exception.UseForbiddenClauseException, lambda: validator.validate())

    def testBlockOpen(self):
        parser = Parser(
            """
a = open
            """
        )
        validator = NodeValidator(parser.parse_tree)
        self.assertRaises(exception.CallForbiddenFunctionException, lambda: validator.validate())

    def testBlockOpen2(self):
        parser = Parser(
            """
a = open('file', 'r')
            """
        )
        validator = NodeValidator(parser.parse_tree)
        self.assertRaises(exception.CallForbiddenFunctionException, lambda: validator.validate())

    def testBlockId(self):
        parser = Parser(
            """
a = id(open)
            """
        )
        validator = NodeValidator(parser.parse_tree)
        self.assertRaises(exception.CallForbiddenFunctionException, lambda: validator.validate())


if __name__ == '__main__':
    unittest.main()
