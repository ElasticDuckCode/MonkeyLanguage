from unittest import main, TestCase
from src.monkey import obj


class TestObj(TestCase):
    def test_obj_hashing(self):
        int_obj = obj.Integer(10)
        str_obj = obj.String("hello")
        int2_obj = obj.Integer(9)
        str2_obj = obj.String("not_hello")
        hash_obj = obj.Hash({str_obj: int_obj, str2_obj: int2_obj})

        # Because using @dataclass generated __hash__, copies of arrays already
        # have desired effect.
        #   1) Different copies of Object with same value hash to same Object
        #   2) Object with different value do not has to same Object
        # So we don't need to implement HashKey()
        # from the book.
        key_obj = obj.String("hello")
        val_obj = obj.Integer(10)
        self.assertEqual(hash_obj.pairs[key_obj], val_obj)
        key_obj = obj.String("not_hello")
        val_obj = obj.Integer(10)
        self.assertNotEqual(hash_obj.pairs[key_obj], val_obj)
        self.assertEqual(hash_obj.inspect, "{hello: 10, not_hello: 9}")
