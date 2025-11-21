#!/usr/bin/python
# Test inventory plugin

from ansible.plugins.inventory import BaseInventoryPlugin

class InventoryModule(BaseInventoryPlugin):
    NAME = 'test_inventory'
    
    def parse(self, inventory, loader, path, cache=True):
        pass
