from pytest import raises
import passive_auto_design.units.physical_dimension as phy
from numpy import inf, all


def test_physical_dimension():
    Phy = phy.PhysicalDimension(value=[10, 0], unit="Hz", scale="lin")
    assert Phy.shape() == (2,)
    assert isinstance(Phy.dB(), phy.PhysicalDimension)
    assert Phy.dB() == phy.PhysicalDimension(value=[10, -inf], unit="Hz", scale="dB")
    assert 2*Phy == phy.PhysicalDimension(value=[20, 0], unit="Hz", scale="lin")

    with raises(ValueError):
        Phy = phy.PhysicalDimension(value="ab", unit="Hz", scale="lin")
