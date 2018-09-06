import sys
import itertools
import pathlib
import skimage.io
import skimage.external.tifffile
import numpy as np
import xml.etree.cElementTree as ElementTree


ometiff_path = sys.argv[1]

output_base_path = pathlib.Path('mist-files')
output_base_path.mkdir(exist_ok=True)

output_pattern = 'mist_r{row:03}_c{col:03}.tif'

tf = skimage.external.tifffile.TiffFile(ometiff_path)
xml = tf.pages[0].tags['image_description'].value
ome_root = ElementTree.fromstring(xml)
plane_elts = ome_root.findall(
    'ome:Image/ome:Pixels/ome:Plane',
    {'ome': 'http://www.openmicroscopy.org/Schemas/OME/2016-06'}
)
positions = np.array([
    [float(p.get('PositionX')), float(p.get('PositionY'))] for p in plane_elts
])
shape = np.array([len(set(positions[:, d])) for d in [0, 1]])
if np.prod(shape) != len(positions):
    raise ValueError("Series positions do not form a grid")

rc_grid = itertools.product(range(shape[1]), range(shape[0]))
for i, (r, c) in enumerate(rc_grid):
    img = skimage.io.imread(ometiff_path, series=i)
    output_path = output_base_path / output_pattern.format(row=r, col=c)
    skimage.io.imsave(output_path, img)
