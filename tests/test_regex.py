import unittest
from assertpy import assert_that
import re


class TestRegex(unittest.TestCase):
    def test_Regex01(self):
        try:
            print("test_Regex01 Inicio")
            valor = "1"
            pattern = re.compile("([01])", re.IGNORECASE)

            assert_that(pattern.match("1") != None)
            assert_that(pattern.match("0") != None)
            assert_that(pattern.match("a") == None)
        except Exception as ex:
            print(ex)
            assert_that(False)
        finally:
            print("test_Regex01 Fin")
