"""
File:test_basic.py
Author:laoyang
"""
import unittest
from module_foo import sayhello

class SayHelloTestCase(unittest.TestCase):
    """测试用例"""
    def setUp(self):
        """测试固件->测试前"""
        pass

    def tearDown(self):
        """测试固件 -> 测试后"""
        pass

    def test_sayhello(self):
        """测试sayhello"""
        rv = sayhello()
        self.assertEqual(rv,'Hello!')

    def test_sayhello_to_somebody(self):
        rv = sayhello(to="laoyang")
        self.assertEqual(rv,'Hello, laoyang!')


if __name__ == '__main__':
    unittest.main()