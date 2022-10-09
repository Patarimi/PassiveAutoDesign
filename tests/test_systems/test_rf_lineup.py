from pytest import raises
from passive_auto_design.units.noise import NoiseFigure
from passive_auto_design.units.time import Frequency
from passive_auto_design.units.physical_dimension import PhysicalDimension
import passive_auto_design.system.rf_line_up as lu


def test_friis():
    noise_factor = NoiseFigure([3, 6])
    gain = PhysicalDimension(value=15, scale="dB")
    f_out = lu.friis(noise_factor, gain)
    assert round(f_out, 2) == NoiseFigure(3.2)
    gain = PhysicalDimension(value=[15, 18], scale="dB")
    with raises(ValueError):
        lu.friis(noise_factor, gain)


def test_rf_bloc():
    with raises(ValueError):
        lu.RFBloc(
            freq=Frequency(value=2e9),
            gain=PhysicalDimension(value=[1, 2]),
            noise=NoiseFigure(value=[1, 5]),
        )
    lu.RFBloc(
        freq=Frequency(value=[2e9, 1e9]),
        gain=PhysicalDimension(value=[1, 2]),
        noise=NoiseFigure(value=[1, 5]),
    )


def test_rf_lin_up():
    b1 = lu.RFBloc(
        freq=Frequency(value=1e9),
        gain=PhysicalDimension(value=15, scale="dB"),
        noise=NoiseFigure(value=3),
    )
    b2 = lu.RFBloc(
        freq=Frequency(value=2e9),
        gain=PhysicalDimension(value=9, scale="dB"),
        noise=NoiseFigure(value=6),
    )

    RF_LU = lu.RFLineUp(chain=(b1, b2))
    assert round(RF_LU.NF(), 1) == NoiseFigure(3.2)
    assert RF_LU.gain() == 24
