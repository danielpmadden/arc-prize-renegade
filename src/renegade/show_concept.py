import argparse,json
from .knowledge import load_knowledge
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument('identifier');a=p.parse_args(argv)
 for item in load_knowledge()[0]:
  if item.identifier==a.identifier: print(json.dumps(item.__dict__ | {'maturity':item.maturity.value},sort_keys=True,default=list)); return 0
 p.error('unknown concept')
if __name__=='__main__': raise SystemExit(main())
