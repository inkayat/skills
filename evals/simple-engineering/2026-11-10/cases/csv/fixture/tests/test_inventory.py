import unittest
from inventory import parse_inventory
from importer import import_inventory
from preview import preview_inventory

class ExistingInventoryTests(unittest.TestCase):
    def test_preview(self):
        self.assertEqual(preview_inventory("name,quantity\napple,2\npear,3\n"), {"rows":2,"units":5})
    def test_import(self):
        stock = {"apple":1}
        self.assertEqual(import_inventory("name,quantity\napple,2\n", stock), 1)
        self.assertEqual(stock, {"apple":3})
    def test_invalid_quantity(self):
        with self.assertRaises(ValueError):
            parse_inventory("name,quantity\napple,-2\n")
