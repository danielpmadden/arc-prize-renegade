"""Concise command line inspection for the typed grammar."""
from __future__ import annotations
import argparse,json
from .grammar import DEFAULT_REGISTRY, validate_registry
from .composition_curriculum import evaluate_curriculum
def main(argv=None):
 p=argparse.ArgumentParser(); p.add_argument("command",choices=("inspect","validate","curriculum","telemetry")); p.add_argument("--json",action="store_true"); args=p.parse_args(argv)
 if args.command in {"inspect","validate"}: payload=validate_registry(DEFAULT_REGISTRY)
 else: payload=evaluate_curriculum()
 print(json.dumps(payload,sort_keys=True,separators=(",",":")) if args.json else payload)
 return 0
if __name__ == "__main__": raise SystemExit(main())
