"""Executable demonstration of deterministic observation and measurement handling."""

from .core import Capability, Executive, Memory
from .foundation import StableIdentifier
from .measurements import measure_dimensions
from .observations import Observation, ObservationFrame, ObservationKind


def main() -> None:
    """Run an explicit observation-frame measurement example."""
    memory = Memory()
    memory.remember_capability(
        Capability(
            name="measure_dimensions",
            description="Measure supplied tuple-grid height and width.",
            function=measure_dimensions,
        )
    )
    observation = Observation(
        identity=StableIdentifier("observation", "example-grid", 1),
        kind=ObservationKind.STRUCTURED,
        value=(("red", "red"), ("blue", "red")),
        source="module demonstration",
    )
    frame = ObservationFrame(
        identity=StableIdentifier("frame", "example-grid", 1), observations=(observation,)
    )
    workspace = Executive(memory).solve(frame, "measure_dimensions")

    print("ARC Prize Renegade")
    print("-------------------")
    for event in workspace.trace:
        print(f"{event.sequence}. [{event.kind.value}] {event.message}")
    print(f"Measurement: {workspace.result.value}")


if __name__ == "__main__":
    main()
