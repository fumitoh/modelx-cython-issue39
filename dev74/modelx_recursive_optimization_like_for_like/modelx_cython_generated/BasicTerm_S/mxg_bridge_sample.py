from pathlib import Path
import pickle
from BasicTerm_S_mxg_f32da97f78_nomx import mx_model
root = Path(__file__).resolve().parent
points = pickle.loads((root / 'sample_points.pkl').read_bytes())
cell_args = pickle.loads((root / 'cell_args.pkl').read_bytes())
for point in points:
    space = mx_model
    space = getattr(space, 'Projection')
    item = space[point[0]]
    cell = getattr(item, 'pv_net_cf')
    cell(*cell_args)
