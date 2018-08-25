import numbers
import attr
import numpy as np


v_float = attr.validators.instance_of(numbers.Real)
v_int = attr.validators.instance_of(numbers.Integral)
v_array = attr.validators.instance_of(np.ndarray)
v_dtype = attr.validators.instance_of(np.dtype)


@attr.s
class Stage:
    x = attr.ib(validator=v_float)
    y = attr.ib(validator=v_float)

    @property
    def position(self):
        return np.array([self.x, self.y])

    def goto(self, x, y):
        self.x = x + np.random.rand() * 30
        self.y = y + np.random.rand() * 30



@attr.s
class Camera:
    # Unit is pixels.
    width = attr.ib(validator=v_int)
    height = attr.ib(validator=v_int)
    # Unit is microns/pixel.
    scale = attr.ib(validator=v_float)
    image = attr.ib(validator=v_array)
    stage = attr.ib(validator=attr.validators.instance_of(Stage))

    @property
    def dtype(self):
        return self.image.dtype

    @property
    def dtype_range(self):
        if np.issubdtype(self.dtype, np.integer):
            info = np.iinfo(self.dtype)
            return (info.min, info.max)
        elif np.issubdtype(self.dtype, np.floating):
            return (0, 1)
        else:
            raise ValueError("Unhandled dtype")

    def acquire(self):
        lower = self.stage.position / self.scale
        upper = lower + [self.width, self.height]
        x1, y1 = lower.astype(int)
        x2, y2 = upper.astype(int)
        a = self.image[y1:y2, x1:x2]
        return a


@attr.s
class Actuator:
    pass


@attr.s
class Acquisition:
    x = attr.ib(validator=v_float)
    y = attr.ib(validator=v_float)
    image = attr.ib(validator=v_array)
