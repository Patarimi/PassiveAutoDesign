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
        raise ValueError(f"cannot coerse input of type {type(v)} to numpy array.")


class PhysicalDimension(BaseModel):
    value: NDArray
    unit: str = ""
    scale: Literal["lin", "dB"] = "lin"

    class Config:
        arbitrary_types_allowed = True

    def dB(self):
        """
        Return the decibel value of the given imaginary number.
        """
        v = self.value
        v_db = v if self.scale == "dB" else 10 * np.log10(np.abs(v))
        out = self.__class__(value=v_db, scale="dB", unit=self.unit)
        return out

    def lin(self):
        """
        return the linear magnitude of the given magnitude in decibel
        """
        v = self.value
        v_lin = 10 ** (v / 10) if self.scale == "dB" else v
        return self.__class__(value=v_lin, scale="lin", unit=self.unit)

    def __getitem__(self, item):
        return self.__class__(
            value=[
                self.value[item],
            ],
            scale=self.scale,
            unit=self.unit,
        )

    def shape(self):
        return self.value.shape

    def __sub__(self, other):
        return operator(self, other, "-")

    def __add__(self, other):
        return operator(self, other, "+")

    def __truediv__(self, other):
        return operator(self, other, "/")

    def __mul__(self, other):
        return operator(self, other, "*")

    def __eq__(self, other):
        return (
            self.unit == other.unit
            and self.scale == other.scale
            and np.all(self.value == other.value)
        )

    def __round__(self, x):
        return self.__class__(
            value=np.round(self.value, x), scale=self.scale, unit=self.unit
        )


def operator(l_a, l_b, op):
    b = l_b.value if isinstance(l_b, PhysicalDimension) else l_b
    if op == "+":
        res = l_a.value + b
    if op == "-":
        res = l_a.value - b
    if op == "/":
        res = l_a.value / b
    if op == "*":
        res = l_a.value * b
    return l_a.__class__(value=res, scale=l_a.scale, unit=l_a.unit)
