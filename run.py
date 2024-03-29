import sys
import pathlib
import io
import uuid
import numpy as np
import skimage.io
from models import *


sample_pathname = sys.argv[1]
output_pathname = 'simulated-input.ome.tif'

sample_path = pathlib.Path(sample_pathname).expanduser().resolve()
output_path = pathlib.Path(output_pathname).expanduser().resolve()

sample_image = skimage.io.imread(str(sample_path))

stage = Stage(x=0, y=0)
camera = Camera(
    width=800, height=800, scale=1.0, image=sample_image, noise_std=50,
    stage=stage
)

origin_x = 600
origin_y = 0
roi_width = camera.width * 3
roi_height = camera.height * 2
pitch = int(camera.width * 0.90)

slice_x = slice(origin_x, origin_x + roi_width, pitch)
slice_y = slice(origin_y, origin_y + roi_height, pitch)
positions = np.mgrid[slice_x, slice_y].T.reshape(-1,2)
num_positions = len(positions)
acquisitions = [None] * num_positions
true_positions = np.zeros((num_positions, 2))
for i, (x, y) in enumerate(positions):
    stage.goto(x, y)
    acquisitions[i] = Acquisition(x, -y, camera.acquire())
    true_positions[i] = stage.position

print("True stage positions:")
print(np.array_str(true_positions, suppress_small=True))
np.savetxt('true-positions.csv', true_positions, delimiter=',')

img_uuid = uuid.uuid4().urn
xml = io.StringIO()
xml.write('<?xml version="1.0" encoding="UTF-8"?>')
xml.write(
    f'<OME xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06"'
    f' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
    f' UUID="{img_uuid}"'
    f' xsi:schemaLocation="http://www.openmicroscopy.org/Schemas/OME/2016-06'
    f' http://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd">'
)
for i, ac in enumerate(acquisitions):
    xml.write(
        f'<Image ID="Image:{i}">'
    )
    xml.write(
        f'<Pixels BigEndian="false" DimensionOrder="XYZCT" ID="Pixels:{i}"'
        f' PhysicalSizeX="{camera.scale}" PhysicalSizeXUnit="µm"'
        f' PhysicalSizeY="{camera.scale}" PhysicalSizeYUnit="µm"'
        f' PhysicalSizeZ="1.0" PhysicalSizeZUnit="µm"'
        f' SizeC="1" SizeT="1"'
        f' SizeX="{ac.image.shape[1]}" SizeY="{ac.image.shape[0]}" SizeZ="1"'
        f' Type="{ac.image.dtype.name}">'
    )
    xml.write(
        f'<Channel ID="Channel:{i}:0" SamplesPerPixel="1"><LightPath/></Channel>'
    )
    xml.write(
        f'<TiffData FirstC="0" FirstT="0" FirstZ="0" IFD="{i}" PlaneCount="1">'
        f'<UUID FileName="{output_path.name}">{img_uuid}</UUID>'
        f'</TiffData>'
    )
    xml.write(
        f'<Plane'
        f' PositionX="{ac.x}" PositionXUnit="µm"'
        f' PositionY="{ac.y}" PositionYUnit="µm"'
        f' PositionZ="0.0" PositionZUnit="µm"'
        f' TheC="0" TheT="0" TheZ="0"/>'
    )
    xml.write('</Pixels>')
    xml.write('</Image>')
xml.write('</OME>')


skimage.io.imsave(
    str(output_path),
    np.array([ac.image for ac in acquisitions]),
    description=xml.getvalue().encode('utf-8')
)
