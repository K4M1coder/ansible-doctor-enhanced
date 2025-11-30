#!/usr/bin/python
# Test filter plugin


class FilterModule:
    def filters(self):
        return {"test_filter": lambda x: x}
