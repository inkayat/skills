"""Additional diagnostics discovered by blind review, not predeclared grading."""
from pathlib import Path
import sys
import unittest

TARGET = Path(sys.argv.pop(1)).resolve()
sys.path.insert(0, str(TARGET))


class PosthocCsvDiagnostics(unittest.TestCase):
    def test_unquoted_whitespace_rows_keep_existing_compatibility(self):
        from inventory import parse_inventory
        from importer import import_inventory
        text = 'name,quantity\n   \napple,2\n\t\n'
        self.assertEqual(parse_inventory(text), [('apple', 2)])
        stock = {'old': 9}
        self.assertEqual(import_inventory(text, stock), 1)
        self.assertEqual(stock, {'old': 9, 'apple': 2})

    def test_quoted_single_space_is_invalid_and_import_stays_unchanged(self):
        from inventory import parse_inventory
        from importer import import_inventory
        text = 'name,quantity\napple,2\n" "\n'
        with self.assertRaises(ValueError):
            parse_inventory(text)
        stock = {'old': 9}
        with self.assertRaises(ValueError):
            import_inventory(text, stock)
        self.assertEqual(stock, {'old': 9})

    def test_malformed_upload_keeps_stock_unchanged_independently(self):
        from importer import import_inventory
        stock = {'old': 9}
        rejected = False
        try:
            import_inventory('name,quantity\napple,2\n" "\n', stock)
        except ValueError:
            rejected = True
        self.assertEqual(stock, {'old': 9})
        self.assertTrue(rejected, 'Malformed upload was not rejected')


if __name__ == '__main__':
    unittest.main(verbosity=2)
