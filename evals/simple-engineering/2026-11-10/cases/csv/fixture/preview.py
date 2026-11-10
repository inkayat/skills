from inventory import parse_inventory

def preview_inventory(text):
    rows = parse_inventory(text)
    return {"rows":len(rows), "units":sum(qty for _, qty in rows)}
