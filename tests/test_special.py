import pytest
import passive_auto_design.special as sp

def test_special():
    with pytest.raises(ValueError):
        assert sp.std_dev((20+1j*40, 20+1j*40), 50)
    assert sp.qual_f(100 - 1j*300) == -3.0
