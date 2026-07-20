"""
ARC Prize Renegade

A deterministic symbolic reasoning system built from the ground up.

This file is intentionally small. It establishes the first executable
reasoning cycle before the project is divided into packages and modules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class Observation:
    """Something presented to the system."""

    name: str
    value: Any


@dataclass(frozen=True)
class Capability:
    """A deterministic operation the system knows how to perform."""

    name: str
    description: str
    function: Callable[[Any], Any]

    def execute(self, value: Any) -> Any:
        return self.function(value)


@dataclass
class Memory:
    """Persistent knowledge available to the reasoning system."""

    capabilities: dict[str, Capability] = field(default_factory=dict)
    history: list[str] = field(default_factory=list)

    def remember_capability(self, capability: Capability) -> None:
        self.capabilities[capability.name] = capability

    def record(self, event: str) -> None:
        self.history.append(event)


@dataclass
class Workspace:
    """The active state of the current reasoning attempt."""

    observation: Observation
    result: Any | None = None
    trace: list[str] = field(default_factory=list)

    def record(self, event: str) -> None:
        self.trace.append(event)


class Executive:
    """Selects and applies relevant capabilities deterministically."""

    def __init__(self, memory: Memory) -> None:
        self.memory = memory

    def solve(self, observation: Observation, capability_name: str) -> Workspace:
        workspace = Workspace(observation=observation)
        workspace.record(f"Observed: {observation.name} = {observation.value!r}")

        capability = self.memory.capabilities.get(capability_name)

        if capability is None:
            workspace.record(f"Capability not found: {capability_name}")
            return workspace

        workspace.record(f"Selected capability: {capability.name}")
        workspace.result = capability.execute(observation.value)
        workspace.record(f"Result: {workspace.result!r}")

        self.memory.record(
            f"{capability.name} applied to {observation.name}"
        )

        return workspace


def double_number(value: Any) -> Any:
    if not isinstance(value, int):
        raise TypeError("double_number requires an integer")

    return value * 2


def main() -> None:
    memory = Memory()

    memory.remember_capability(
        Capability(
            name="double_number",
            description="Multiply an integer by two.",
            function=double_number,
        )
    )

    executive = Executive(memory)

    observation = Observation(
        name="example_number",
        value=4,
    )

    workspace = executive.solve(
        observation=observation,
        capability_name="double_number",
    )

    print("ARC Prize Renegade")
    print("-------------------")

    for event in workspace.trace:
        print(event)


if __name__ == "__main__":
    main()