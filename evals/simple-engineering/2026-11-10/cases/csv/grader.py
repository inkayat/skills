import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
TARGET = Path(sys.argv.pop(1)).resolve()
sys.path.insert(0, str(TARGET))

class Contract(unittest.TestCase):
    def test_quoted_comma_and_newline(self):
        from inventory import parse_inventory
        self.assertEqual(parse_inventory('name,quantity\n"tea, green",2\n"two\nlines",3\n'), [("tea, green",2),("two\nlines",3)])
    def test_preview_consumer(self):
        from preview import preview_inventory
        self.assertEqual(preview_inventory('name,quantity\r\n"tea, green",2\r\n"two\r\nlines",3\r\n'), {"rows":2,"units":5})
    def test_import_consumer(self):
        from importer import import_inventory
        stock = {"tea, green":5}
        self.assertEqual(import_inventory('name,quantity\n"tea, green",2\n"tea, green",3\n',stock),2)
        self.assertEqual(stock,{"tea, green":10})
    def test_validation_and_atomicity(self):
        from importer import import_inventory
        invalid = ["bad,-1", "bad,1.5", "bad,+2", "bad, 2", "bad,١", " ,2", "too,many,columns"]
        for row in invalid:
            with self.subTest(row=row):
                stock={"old":9}
                with self.assertRaises(ValueError):
                    import_inventory("name,quantity\nnew,2\n"+row+"\n",stock)
                self.assertEqual(stock,{"old":9})
    def test_escaped_quotes_blank_rows_and_zero(self):
        from inventory import parse_inventory
        self.assertEqual(parse_inventory('name,quantity\n\n"say ""hello""",0\n'), [('say "hello"',0)])
    def test_header_and_field_validation(self):
        from inventory import parse_inventory
        for text in ["", "wrong,header\na,2\n", "name,quantity\na\n"]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_inventory(text)

if __name__ == "__main__":
    unittest.main(verbosity=2)
