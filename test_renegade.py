"""Tests for the first ARC Prize Renegade reasoning cycle."""

import unittest

from renegade import (
    Capability,
    Executive,
    Memory,
    Observation,
    double_number,
)


class RenegadeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.memory = Memory()

        self.memory.remember_capability(
            Capability(
                name="double_number",
                description="Multiply an integer by two.",
                function=double_number,
            )
        )

        self.executive = Executive(self.memory)

    def test_capability_is_remembered(self) -> None:
        self.assertIn("double_number", self.memory.capabilities)

    def test_observation_is_processed(self) -> None:
        observation = Observation(
            name="test_number",
            value=5,
        )

        workspace = self.executive.solve(
            observation=observation,
            capability_name="double_number",
        )

        self.assertEqual(workspace.result, 10)

    def test_missing_capability_is_reported(self) -> None:
        observation = Observation(
            name="test_number",
            value=5,
        )

        workspace = self.executive.solve(
            observation=observation,
            capability_name="unknown_capability",
        )

        self.assertIsNone(workspace.result)
        self.assertIn(
            "Capability not found: unknown_capability",
            workspace.trace,
        )

    def test_invalid_input_is_rejected(self) -> None:
        observation = Observation(
            name="invalid_value",
            value="five",
        )

        with self.assertRaises(TypeError):
            self.executive.solve(
                observation=observation,
                capability_name="double_number",
            )

    def test_execution_is_deterministic(self) -> None:
        observation = Observation(
            name="repeatable_number",
            value=8,
        )

        first_run = self.executive.solve(
            observation=observation,
            capability_name="double_number",
        )

        second_run = self.executive.solve(
            observation=observation,
            capability_name="double_number",
        )

        self.assertEqual(first_run.result, second_run.result)
        self.assertEqual(first_run.trace, second_run.trace)

    def test_successful_execution_enters_history(self) -> None:
        observation = Observation(
            name="remembered_number",
            value=3,
        )

        self.executive.solve(
            observation=observation,
            capability_name="double_number",
        )

        self.assertEqual(
            self.memory.history,
            ["double_number applied to remembered_number"],
        )


if __name__ == "__main__":
    unittest.main()