def parse_inventory(text):
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines or lines[0] != "name,quantity":
        raise ValueError("Expected name,quantity header")
    result = []
    for line in lines[1:]:
        fields = line.split(",")
        if len(fields) != 2:
            raise ValueError("Expected two columns")
        name, raw = fields
        if not name.strip() or not raw.isascii() or not raw.isdigit():
            raise ValueError("Expected a name and non-negative whole quantity")
        result.append((name, int(raw)))
    return result
