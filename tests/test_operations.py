"""Architecture contracts for the executable-operation inventory."""

import unittest

from renegade.operations import OPERATION_SPECS, operation_inventory
from renegade.solver import SUPPORTED_OPERATION_NAMES


class OperationInventoryTests(unittest.TestCase):
    def test_inventory_matches_executor_contract(self):
        """Every documented operation is executable, and none is omitted."""
        self.assertEqual(set(OPERATION_SPECS), SUPPORTED_OPERATION_NAMES)
        self.assertEqual(
            [spec["name"] for spec in operation_inventory()],
            [spec.name for spec in OPERATION_SPECS.values()],
        )
