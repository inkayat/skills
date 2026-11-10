from inventory import parse_inventory

def import_inventory(text, stock):
    rows = parse_inventory(text)
    for name, qty in rows:
        stock[name] = stock.get(name, 0) + qty
    return len(rows)
