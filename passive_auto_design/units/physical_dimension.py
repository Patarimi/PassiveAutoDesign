from typing import Literal, List, Tuple
from pydantic import BaseModel
import numpy as np


class NDArray(np.ndarray):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, NDArray):
            return v
        if isinstance(v, np.ndarray):
            return v
        if isinstance(v, List) or isinstance(v, Tuple):
            return np.asarray(v)
        if (
            isinstance(v, float)
            or isinstance(v, np.float32)
            or isinstance(v, np.float64)
            or isinstance(v, int)
            or isinstance(v, np.int32)
            or isinstance(v, np.int64)
            or isinstance(v, complex)
            or isinstance(v, np.complex64)
            or isinstance(v, np.complex128)
        ):
            return np.asarray(
                [
                    v,
                ]
            )
        raise ValueError(f"cannot coerse input of type {type(v)} to numpy array.")


class PhysicalDimension(BaseModel):
    """
    Pydantic model adding unit and scale to standard ndarray.
    """

    value: NDArray
    unit: str = ""
    scale: Literal["lin", "dB"] = "lin"

    class Config:
        arbitrary_types_allowed = True

    def dB(self):
        """
        Convert the Physical dimension to decibel.
        """
        v = self.value
        v_db = v if self.scale == "dB" else 10 * np.log10(np.abs(v))
        out = self.__class__(value=v_db, scale="dB", unit=self.unit)
        return out

    def lin(self):
        """
        Convert the Physical dimension to linear magnitude.
        """
        v = self.value
        v_lin = 10 ** (v / 10) if self.scale == "dB" else v
        return self.__class__(value=v_lin, scale="lin", unit=self.unit)

    def __getitem__(self, item):
        return self.__class__(
            value=self.value[item],
            scale=self.scale,
            unit=self.unit,
        )

    def __setitem__(self, key, value):
        self.value[key] = value

    @property
    def shape(self):
        return self.value.shape

    def __sub__(self, other):
        return self.__operator(other, "-")

    def __rsub__(self, other):
        return self.__operator(other, "-") * -1

    def __add__(self, other):
        return self.__operator(other, "+")

    def __radd__(self, other):
        return self.__operator(other, "+")

    def __truediv__(self, other):
        return self.__operator(other, "/")

    def __mul__(self, other):
        return self.__operator(other, "*")

    def __rmul__(self, other):
        return self.__operator(other, "*")

    def __pow__(self, other):
        return self.__operator(other, "**")

    def __eq__(self, other):
        if isinstance(other, PhysicalDimension):
            return (
                self.unit == other.unit
                and self.scale == other.scale
                and np.all(self.value == other.value)
            )
        else:
            return np.all(self.value == other)

    def __lt__(self, other):
        return np.all(self.value < other.value)

    def __round__(self, x):
        return self.__class__(
            value=np.round(self.value, x), scale=self.scale, unit=self.unit
        )

    def rint(self):
        return np.rint(self.value)

    def sqrt(self):
        return np.sqrt(self.value)

    def __operator(self, l_b, op):
        b = l_b.value if isinstance(l_b, PhysicalDimension) else l_b
        if op == "+":
            res = self.value + b
        if op == "-":
            res = self.value - b
        if op == "/":
            res = self.value / b
        if op == "*":
            res = self.value * b
        if op == "**":
            res = self.value**b
        return self.__class__(value=np.array(res), scale=self.scale, unit=self.unit)
