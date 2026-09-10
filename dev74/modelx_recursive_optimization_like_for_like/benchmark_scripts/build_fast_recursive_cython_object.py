from __future__ import annotations
import argparse, json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS = ['BasicTerm_S','Term_UK_A','WOL_UK_S','ULSG_US_S','VA_US_S']

def main() -> int:
    ap=argparse.ArgumentParser();ap.add_argument('models',nargs='*',choices=MODELS);ns=ap.parse_args();models=ns.models or MODELS
    rows=[]; ok=True
    for model in models:
        t=time.perf_counter()
        cp=subprocess.run([sys.executable,'setup.py','build_ext','--inplace',f'MODEL={model}'],cwd=ROOT/'fast_recursive_cython_object',text=True,capture_output=True)
        row={'model':model,'returncode':cp.returncode,'build_s':time.perf_counter()-t,'stdout_tail':cp.stdout[-4000:],'stderr_tail':cp.stderr[-4000:]}
        rows.append(row);print(json.dumps({k:v for k,v in row.items() if not k.endswith('_tail')}),flush=True);ok &= cp.returncode==0
    out=ROOT/'results/FAST_RECURSIVE_CYTHON_OBJECT_BUILD_FRESH.json';out.write_text(json.dumps({'models':rows},indent=2),encoding='utf-8')
    return 0 if ok else 2
if __name__=='__main__':raise SystemExit(main())
