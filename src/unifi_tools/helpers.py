import asyncio
from collections.abc import MutableMapping


class DataStorage(MutableMapping):
    def __init__(self):
        self.data: dict = {}

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return f"{type(self).__name__}({self.data})"


def cancel_tasks():
    for task in asyncio.all_tasks():
        if task.done():
            continue

        task.cancel()
