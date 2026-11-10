# Inventory CSV

Python standard library only. Run `python3 -m unittest discover -s tests -v`.
The header is exactly `name,quantity`. Data rows have two fields.
Names must not be blank; preserve their text, including embedded whitespace.
Quantities are ASCII non-negative whole numbers, without signs or surrounding spaces.
Empty rows may be skipped. Repeated names add their quantities on import.
`parse_inventory(text)` returns (name, quantity) tuples.
`preview_inventory(text)` returns row and total-unit counts.
`import_inventory(text, stock)` adds quantities and returns the imported row count.
Invalid input raises ValueError and must not partially modify stock.
