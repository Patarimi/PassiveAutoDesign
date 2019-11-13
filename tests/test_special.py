import pytest
import numpy as np
from passive_auto_design.special import std_dev

def test_special():
    with pytest.raises(ValueError):
        assert std_dev(np.array([20+1j*40]), np.array([20+1j*40, 50]))