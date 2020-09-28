import passive_auto_design.components.transformer as tf
from skrf import Frequency

def test_transformer():
    """
    unity test for tranformer object
    """
    geo = {'di':20,
           'n_turn':2,
           'width':1e-3,
           'gap':2e-3,
           'height':1e-6}
    transfo = tf.Transformer(geo, geo)
    transfo = tf.Transformer(geo, geo, Frequency(1, 1, 1))
    transfo.set_primary(geo)
    transfo.set_secondary(geo)
    assert transfo.model == {'ls': 0.0001376861381145666,
                             'rs': 0.13257484962738228,
                             'lp': 0.0001376861381145666,
                             'rp': 0.13257484962738228,
                             'k': 0.9,
                             'cg': 8.854187812800001e-05,
                             'cm': 0.0035416751251200005,
                             }
