import passive_auto_design.components.lumped_element as lmp


def test_capacitor():
    """
    unity test for capacitor object
    """
    cap = lmp.Capacitor(1e-6, 1e-3, 1)
    assert cap.model["cap"] == 8.8541878128e-15

    cap.set_model_with_dim({"cap": 1e-15}, "eps_r")
    assert round(cap.const["eps_r"], 6) == 0.112941
    assert round(cap.model["cap"]*1e15, 6) == 1
    assert str(cap) == r"1 fF"


def test_resistor():
    """
    unity test for capacitor object
    """
    res = lmp.Resistor()
    assert res.model == {"res": 1e-12}

    res.set_model_with_dim({"res": 1e3}, "length")
    assert round(res.dim["length"]*1e-12, 4) == 1000
    assert round(res.model["res"], 4) == 1e3
    assert str(res) == r"1 k$\Omega$"


def test_inductor():
    """
    unity test for capacitor object
    """

    ind = lmp.Inductor(d_i=210e-6, n_turn=1, width=10e-6, gap=3e-6)
    assert ind.model["ind"] == 5.356077338175006e-10

    ind = lmp.Inductor(d_i=183e-6, n_turn=2, width=10e-6, gap=3e-6)
    assert ind.model["ind"] == 1.6684854964430778e-09

    ind.set_model_with_dim({"ind": 1.96e-9}, "k_1")
    assert round(ind.const["k_1"], 6) == 2.643116
    assert round(ind.model["ind"]*1e9, 6) == 1.96
    assert str(ind) == "1.96 nH"
