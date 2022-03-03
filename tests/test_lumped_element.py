import passive_auto_design.components.lumped_element as lmp
import passive_auto_design.components.transformer as tf


def test_capacitor():
    """
    unity test for capacitor object
    """
    cap = lmp.Capacitor(1e-6, 1e-3, 1)
    assert cap.par["cap"] == 8.8541878128e-15

    cap.set_x_with_y("eps_r", "cap", 1e-15)
    assert cap.par["eps_r"] == 0.11294090917221976
    assert cap.par["cap"] == 1e-15
    assert str(cap) == r"1 fF"


def test_resistor():
    """
    unity test for capacitor object
    """
    res = lmp.Resistor()
    assert res.par["res"] == 1e-12

    res.set_x_with_y("length", "res", 1e3)
    assert res.par["length"] == 1000000026385065.9
    assert res.par["res"] == 1e3
    assert str(res) == r"1 k$\Omega$"


def test_inductor():
    """
    unity test for capacitor object
    """

    ind = lmp.Inductor(d_i=210e-6, n_turn=1, width=10e-6, gap=3e-6)
    assert ind.par["ind"] == 5.356077338175006e-10

    ind = lmp.Inductor(d_i=183e-6, n_turn=2, width=10e-6, gap=3e-6)
    assert ind.par["ind"] == 1.6684854964430778e-09

    ind.set_x_with_y("k_1", "ind", 1.96e-9)
    assert ind.par["k_1"] == 2.643115627671878
    assert ind.par["ind"] == 1.96e-9
    assert str(ind) == "1.96 nH"


def test_transformer():
    ind1 = lmp.Inductor()
    ind2 = lmp.Inductor()
    transfo = tf.Transformer(ind1, ind2)

    transfo.set_x_with_y("lp.d_i", "lp.ind", 1e-9)
    assert transfo.par["lp"].par["ind"] == 1e-9
