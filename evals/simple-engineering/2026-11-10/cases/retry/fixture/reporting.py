def describe_status(code):
    names = dict()
    names[200] = "ok"
    names[503] = "unavailable"
    if code in names:
        return names[code]
    return "unknown"
