class TemporaryError(Exception):
    pass

def fetch_with_retry(operation, retries=None):
    attempts = (retries or 3) + 1
    for attempt in range(attempts):
        try:
            return operation()
        except TemporaryError:
            if attempt == attempts - 1:
                raise
