"""Executable demonstration of deterministic observation handling."""

from .core import Capability, Executive, Memory
from .foundation import StableIdentifier
from .observations import Observation, ObservationFrame, ObservationKind


def main() -> None:
    """Run a deterministic, minimal observation-frame execution example."""
    memory = Memory()
    memory.remember_capability(
        Capability(
            name="summarize_frame",
            description="Return explicit observation-frame metadata without interpretation.",
            function=lambda frame: {
                "observation_count": len(frame.observations),
                "frame_identity": str(frame.identity),
                "kinds": tuple(item.kind.value for item in frame),
            },
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
    workspace = Executive(memory).solve(frame, "summarize_frame")

    print("ARC Prize Renegade")
    print("-------------------")
    for event in workspace.trace:
        print(f"{event.sequence}. [{event.kind.value}] {event.message}")
    print(f"Summary: {workspace.result}")


if __name__ == "__main__":
    main()
