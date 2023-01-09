import sys
import itertools
import pathlib
import skimage.io
import numpy as np
import tqdm
from ashlar import reg


input_path = pathlib.Path(sys.argv[1])

output_base_path = pathlib.Path(sys.argv[2])
output_base_path.mkdir(exist_ok=True)

output_pattern = 'img_r{row:03}_c{col:03}.tif'

reader = reg.BioformatsReader(str(input_path))
reader.metadata._positions = np.round(reader.metadata.positions, -1)
shape = reader.metadata.grid_dimensions
print(f"Grid shape: {shape}")
(y1, y2), (x1, x2) = [
    sorted(set(reader.metadata.positions[:, d]))[:2] for d in (0, 1)
]
origin = np.array([y1, x1])
step = np.array([y2 - y1, x2 - x1])
rc_coords = np.round((reader.metadata.positions - origin) / step).astype(int)
print("Extracting tiles to TIFFs...")
for i, (r, c) in enumerate(tqdm.tqdm(rc_coords)):
    img = reader.read(i, 0)
    output_path = output_base_path / output_pattern.format(row=r, col=c)
    skimage.io.imsave(output_path, img, check_contrast=False)

print("Use the following MIST parameter settings for this dataset:")
print()
print("  --filenamePattern img_r{rrr}_c{ccc}.tif \\")
print("  --timeSlices 0 \\")
print(f"  --gridWidth {shape[1]} --gridHeight {shape[0]} \\")
print(f"  --extentWidth {shape[1]} --extentHeight {shape[0]}")
