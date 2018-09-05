import numbers
import attr
import numpy as np
import scipy.ndimage


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
        self.x = x + np.random.rand() * 30 - 15
        self.y = y + np.random.rand() * 30 - 15



@attr.s
class Camera:
    # Unit is pixels.
    width = attr.ib(validator=v_int)
    height = attr.ib(validator=v_int)
    # Unit is microns/pixel.
    scale = attr.ib(validator=v_float)
    image = attr.ib(validator=v_array)
    stage = attr.ib(validator=attr.validators.instance_of(Stage))
    noise_std = attr.ib(validator=v_float)

    @property
    def dtype(self):
        return self.image.dtype

    @property
    def dtype_is_int(self):
        return np.issubdtype(self.dtype, np.integer)

    @property
    def dtype_is_float(self):
        return np.issubdtype(self.dtype, np.floating)

    @property
    def dtype_range(self):
        if self.dtype_is_int:
            info = np.iinfo(self.dtype)
            return (info.min, info.max)
        elif self.dtype_is_float:
            return (0, 1)
        else:
            raise ValueError("Unhandled dtype")

    def acquire(self, position=None):
        if position is None:
            position = self.stage.position
        lower, lower_f = np.divmod(np.array(position) / self.scale, 1)
        subpixel_shift = -lower_f[::-1]
        lower = lower.astype(int)
        upper = lower + [self.width, self.height]
        lower -= 1
        upper += 1
        x1, y1 = lower
        x2, y2 = upper
        pad_left = pad_right = pad_top = pad_bottom = 0
        if x1 < 0:
            pad_left = -x1
            x1 = 0
        if y1 < 0:
            pad_top = -y1
            y1 = 0
        if x2 > self.image.shape[1]:
            pad_right = x2 - self.image.shape[1]
            x2 = self.image.shape[1]
        if y2 > self.image.shape[0]:
            pad_bottom = y2 - self.image.shape[0]
            y2 = self.image.shape[0]
        padding = ((pad_top, pad_bottom), (pad_left, pad_right))
        a = self.image[y1:y2, x1:x2]
        a = np.pad(a, padding, 'constant')
        a = scipy.ndimage.shift(a, subpixel_shift)
        a = a[1:-1, 1:-1]
        assert a.shape == (self.height, self.width)
        a = a + np.random.randn(*a.shape) * self.noise_std
        a = a.clip(*self.dtype_range)
        if self.dtype_is_int:
            a = a.round()
        a = a.astype(self.dtype)
        return a


@attr.s
class Actuator:
    pass


@attr.s
class Acquisition:
    x = attr.ib(validator=v_float)
    y = attr.ib(validator=v_float)
    image = attr.ib(validator=v_array)
