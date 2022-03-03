import passive_auto_design.components.transformer as tf
import passive_auto_design.components.lumped_element as lmp
from skrf import Frequency


def test_transformer():
    ind1 = lmp.Inductor(d_i=210e-6, n_turn=1, width=10e-6, gap=3e-6)
    ind2 = lmp.Inductor()
    transfo = tf.Transformer(ind1, ind2)
    assert transfo.par['lp'].par["ind"] == 5.356077338175006e-10

    transfo.set_x_with_y("lp.d_i", "lp.ind", 0.5e-9)
    assert transfo.par["lp"].par["ind"] == 0.5e-9
    assert transfo.par["lp"].par["d_i"] == 197.14500527543268e-6
    assert transfo.calc_ref_value() == 0.8698824082661091
