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
        self.assertRaises(exception.TryImportException, lambda: validator.validate())

    def testBlockImport2(self):
        parser = Parser(
            """
1+2
import ast
            """
        )
        validator = NodeValidator(parser.parse_tree)
        self.assertRaises(exception.TryImportException, lambda: validator.validate())


if __name__ == '__main__':
    unittest.main()
