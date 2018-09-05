import sys
import itertools
import pathlib
import skimage.io

sample_pathname = sys.argv[1]

sample_path = pathlib.Path(sample_pathname).expanduser().resolve()

output_pattern = 'mist_{i:04}.tif'

for i in itertools.count():
    try:
        img = skimage.io.imread(str(sample_path), series=i)
    except IndexError:
        break
    output_path = output_pattern.format(i=i)
    skimage.io.imsave(output_path, img)
