from pathlib import Path
import pickle
from WOL_UK_S_mxg_96ebab816f_nomx import mx_model
root = Path(__file__).resolve().parent
points = pickle.loads((root / 'sample_points.pkl').read_bytes())
cell_args = pickle.loads((root / 'cell_args.pkl').read_bytes())
for point in points:
    space = mx_model
    space = getattr(space, 'Projection')
    item = space[point[0]]
    cell = getattr(item, 'bench_net_cf')
    cell(*cell_args)
