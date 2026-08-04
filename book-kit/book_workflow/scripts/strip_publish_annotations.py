from pathlib import Path
import argparse
import json
import re
import sys

def main(argv=None):
    root = Path(argv[0] if argv else ".")
    out = root / "exports" / "clean"
    out.mkdir(parents=True, exist_ok=True)
    stripped, no_op = [], []
    for src in sorted((root / "chapters").glob("ch-*.md")):
        data = src.read_bytes().decode("utf-8")
        clean = re.sub(r"<!--.*?-->", "", data, flags=re.DOTALL).encode("utf-8")
        dst = out / src.name
        if dst.exists() and dst.read_bytes() == clean: no_op.append(src.name)
        else: dst.write_bytes(clean); stripped.append(src.name)
    print(json.dumps({"stripped": stripped, "no_op": no_op}, sort_keys=True))
    return 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
