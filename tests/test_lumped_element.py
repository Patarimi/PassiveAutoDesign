import passive_auto_design.structure.lumped_element as LMP

def test_capacitor():
    """
    unity test for capacitor object
    """
    cap = LMP.Capacitor(1e-6, 1e-3, 1)
    assert cap.par["cap"] == 8.8541878128e-15

    cap.set_x_with_y("eps_r", "cap", 1e-15)
    assert cap.par["eps_r"] == 0.11294090917221976
    assert cap.par["cap"] == 1e-15

def test_resistor():
    """
    unity test for capacitor object
    """
    res = LMP.Resistor()
    assert res.par["res"] == 1e-12

    res.set_x_with_y("length", "res", 1e3)
    assert res.par["length"] == 1000000026385065.9
    assert res.par["res"] == 1e3

def test_inductor():
    """
    unity test for capacitor object
    """
    ind = LMP.Inductor()
    assert ind.par["ind"] == 1.5432565424041825e-10

    ind.set_x_with_y("k_1", "ind", 1e-9)
    assert ind.par["k_1"] == 8.196952235094303
    assert ind.par["ind"] == 1e-9
    
    ind.set_x_with_y(("k_1", "k_2"), "ind", 300e-12)
    assert ind.par["ind"] == 300e-12

def test_mutual():
    ind1 = LMP.Inductor()
    ind2 = LMP.Inductor()
    mut = LMP.Mutual(ind1, ind2)
    
    assert round(mut.par["k"], 6) == 6e-6
