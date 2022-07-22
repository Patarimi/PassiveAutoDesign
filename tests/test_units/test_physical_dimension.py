from pytest import raises
import passive_auto_design.units.physical_dimension as phy
from numpy import inf, all


def test_physical_dimension():
    Phy = phy.PhysicalDimension(value=[10, 0, 1j * 5], unit="Hz", scale="lin")
    assert Phy.shape == (3,)
    assert isinstance(Phy.dB(), phy.PhysicalDimension)
    assert round(Phy.dB(), 2) == phy.PhysicalDimension(
        value=[10, -inf, 6.99], unit="Hz", scale="dB"
    )
    assert 2 * Phy == phy.PhysicalDimension(
        value=[20, 0, 1j * 10], unit="Hz", scale="lin"
    )

    Phy[2] = 4
    with raises(ValueError):
        Phy = phy.PhysicalDimension(value="ab", unit="Hz", scale="lin")
