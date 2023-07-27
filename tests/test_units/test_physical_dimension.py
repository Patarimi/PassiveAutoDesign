from pytest import raises
import passive_auto_design.units.physical_dimension as phy
from numpy import inf


def test_physical_dimension():
    phys = phy.PhysicalDimension(value=[10, 0, 1j * 5], unit="Hz", scale="lin")
    assert phys.shape == (3,)
    assert isinstance(phys.dB(), phy.PhysicalDimension)
    assert round(phys.dB(), 2) == phy.PhysicalDimension(
        value=[10, -inf, 6.99], unit="Hz", scale="dB"
    )
    assert 2 * phys == phy.PhysicalDimension(
        value=[20, 0, 1j * 10], unit="Hz", scale="lin"
    )

    phys[2] = 4
    with raises(ValueError):
        phy.PhysicalDimension(value="ab", unit="Hz", scale="lin")
