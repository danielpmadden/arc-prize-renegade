"""Executable demonstration of the first Renegade reasoning cycle."""

from .core import Capability, Executive, Memory, Observation, double_number
from .foundation import StableIdentifier


def main() -> None:
    """Run a deterministic, minimal capability execution example."""
    memory = Memory()
    memory.remember_capability(
        Capability(
            name="double_number",
            description="Multiply an integer by two.",
            function=double_number,
            identity=StableIdentifier("capability", "double_number", 1),
        )
    )
    workspace = Executive(memory).solve(
        Observation(name="example_number", value=4), "double_number"
    )

    print("ARC Prize Renegade")
    print("-------------------")
    for event in workspace.trace:
        print(f"{event.sequence}. [{event.kind.value}] {event.message}")


if __name__ == "__main__":
    main()
