import passive_auto_design.components.transformer as tf
import passive_auto_design.components.lumped_element as lmp
from skrf import Frequency


def test_transformer():
    ind1 = lmp.Inductor(d_i=210e-6, n_turn=1, width=10e-6, gap=3e-6)
    ind2 = lmp.Inductor()
    transfo = tf.Transformer(ind1, ind2)
    assert transfo.model['lp'] == 5.356077338175006e-10

    transfo.set_model_with_dim({"lp": 0.5e-9}, "lp.d_i")
    assert round(transfo.model["lp"]*1e9, 6) == 0.5
    assert round(transfo.dim["lp.d_i"]*1e6, 6) == 197.145007
    assert round(transfo.model["k"], 6) == 0.869882
