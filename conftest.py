def pytest_ignore_collect(collection_path, path=None, config=None):  # pragma: no cover - pytest hook
    p = str(collection_path).replace("\\", "/")
    if "/99_doc/" in p:
        return True
    return False

