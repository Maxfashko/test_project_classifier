from typing import Union

import jsonpickle
import numpy as np


class BBox:
    """This is the base class of all bounding boxes.
        The canonical representation is as four points, with no restrictions on their ordering.
        Convenience properties are provided to get the left, bottom, right and top edges and width and height,
        but these are not stored explicitly.

    Args:
        x1: The first of the pair of x coordinates that define the bounding box.
            This is not guaranteed to be less than x1 (for that, use xmin).
        y1: The first of the pair of y coordinates that define the bounding box.
            This is not guaranteed to be less than y1 (for that, use ymin).
        x2: The second of the pair of x coordinates that define the bounding box.
            This is not guaranteed to be greater than x0 (for that, use xmax).
        y2: The second of the pair of y coordinates that define the bounding box.
            This is not guaranteed to be greater than y0 (for that, use ymax).
    """

    def __init__(self, x1: int, y1: int, x2: int, y2: int) -> None:
        if not isinstance(x1, int):
            raise TypeError("x1 must be int object")
        if not isinstance(x2, int):
            raise TypeError("x2 must be int object")
        if not isinstance(y1, int):
            raise TypeError("y1 must be int object")
        if not isinstance(y2, int):
            raise TypeError("y2 must be int object")

        self._points = np.array([x1, y1, x2, y2])

    @staticmethod
    def from_bounds(x0, y0, width, height):
        """
        (staticmethod) Create a new :class:`Bbox` from *x0*, *y0*,
        *width* and *height*.

        *width* and *height* may be negative.
        """
        return BBox.from_extents(x0, y0, x0 + width, y0 + height)

    @staticmethod
    def from_extents(*args):
        """
        (staticmethod) Create a new Bbox from *left*, *bottom*,
        *right* and *top*.

        The *y*-axis increases upwards.
        """
        points = np.array(args, dtype=int).reshape(2, 2)
        return BBox(x1=int(points[0]), y1=int(points[1]), x2=int(points[2]), y2=int(points[3]))

    # def __format__(self, fmt):
    #     return "Bbox(x0={0.x0:{1}}, y0={0.y0:{1}}, x1={0.x1:{1}}, y1={0.y1:{1}})".format(self, fmt)

    # def __str__(self):
    #     return format(self, "")

    def __repr__(self):
        repr_str = self.__class__.__name__
        repr_str += ("(x1={}, y1={}, x2={}, " "y2={})").format(self.x1, self.y1, self.x2, self.y2)
        return repr_str

    def get_points(self):
        """
        Get the points of the bounding box directly as a numpy array
        of the form: ``[x1, y1, x2, y2]``.
        """
        return self._points

    @property
    def width(self):
        """The (signed) width of the bounding box."""
        points = self.get_points()
        return int(points[2] - points[0])

    @property
    def height(self):
        """The (signed) height of the bounding box."""
        points = self.get_points()
        return int(points[3] - points[1])

    @property
    def x1(self):
        """
        The first of the pair of *x* coordinates that define the bounding box.

        This is not guaranteed to be less than :attr:`x1` (for that, use
        :attr:`xmin`).
        """
        return int(self.get_points()[0])

    @property
    def y1(self):
        """
        The first of the pair of *y* coordinates that define the bounding box.

        This is not guaranteed to be less than :attr:`y1` (for that, use
        :attr:`ymin`).
        """
        return int(self.get_points()[1])

    @property
    def x2(self):
        """
        The second of the pair of *x* coordinates that define the bounding box.

        This is not guaranteed to be greater than :attr:`x0` (for that, use
        :attr:`xmax`).
        """
        return int(self.get_points()[2])

    @property
    def y2(self):
        """
        The second of the pair of *y* coordinates that define the bounding box.

        This is not guaranteed to be greater than :attr:`y0` (for that, use
        :attr:`ymax`).
        """
        return int(self.get_points()[3])

    @property
    def cx(self):
        """
        The center of *x* coordinates that define the bounding box.
        """
        return int(self.x1 + self.width / 2)

    @property
    def cy(self):
        """
        The center of *y* coordinates that define the bounding box.
        """
        return int(self.y1 + self.height / 2)

    def __len__(self):
        return len(self.get_points())

    def clamp(self, image_shape):
        x1 = int(np.clip(self.x1, 0, image_shape[1] - 1))
        x2 = int(np.clip(self.x2, 0, image_shape[1] - 1))
        y1 = int(np.clip(self.y1, 0, image_shape[0] - 1))
        y2 = int(np.clip(self.y2, 0, image_shape[0] - 1))

        return BBox(x1=x1, y1=y1, x2=x2, y2=y2)

    def expand(self, sw: Union[int, float], sh: Union[int, float]):
        """Construct a `Bbox` by expanding this one around its center by the factors *sw* and *sh*.

        Args:
            sw: Scale factor by width.
            sh: Scale factor by height.

        Returns:
            Object of BBox class.
        """
        width = self.width
        height = self.height
        deltaw = (sw * width - width) / 2.0
        deltah = (sh * height - height) / 2.0
        a = np.array([-deltaw, -deltah, deltaw, deltah])
        x1, y1, x2, y2 = self._points + a

        return BBox(x1=int(x1), y1=int(y1), x2=int(x2), y2=int(y2))

    def to_numpy(self):
        return self._points

    def to_str(self):
        return [str(x) for x in [self.x1, self.y1, self.x2, self.y2]]

    def to_list(self):
        return [self.x1, self.y1, self.x2, self.y2]

    def to_pascal(self):
        """The pascal_voc format of a bounding box looks like [x_min, y_min, x_max, y_max].
        """
        return {
            "min_x": int(self.x1),
            "min_y": int(self.y1),
            "max_x": int(self.x2),
            "max_y": int(self.y2),
        }


class BBoxHandler(jsonpickle.handlers.BaseHandler):
    def restore(self, obj):
        return BBox(obj["x1"], obj["y1"], obj["x2"], obj["y2"])

    def flatten(self, obj: BBox, data):  # data contains {}
        data["x1"] = obj.x1
        data["y1"] = obj.y1
        data["x2"] = obj.x2
        data["y2"] = obj.y2
        return data


jsonpickle.handlers.registry.register(BBox, BBoxHandler)
