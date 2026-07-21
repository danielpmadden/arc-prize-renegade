from .knowledge import knowledge_report
import json
def main(): print(json.dumps(knowledge_report(),sort_keys=True,indent=2)); return 0
if __name__ == '__main__': raise SystemExit(main())
