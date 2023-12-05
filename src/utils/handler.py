class DataWriter:
    def __init__(self, path: str) -> None:
        self.path = path
        pass

    def insert(self, data):
        with open(self.path, 'a') as _file:
            _file.write(data)
        return None