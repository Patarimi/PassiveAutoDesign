import numpy as np
from pydantic import BaseModel, model_validator, FieldValidationInfo
from typing import List, Optional
from ..units.time import Frequency
from ..units.physical_dimension import PhysicalDimension
from ..units.noise import NoiseFigure


class RFBloc(BaseModel):
    """
    class used to defined RF-bloc.
    """

    freq: Frequency
    gain: PhysicalDimension
    noise: Optional[NoiseFigure]

    @model_validator(mode="after")
    def check_size(self) -> "RFBloc":
        if self.gain.shape != self.freq.shape or self.noise.shape != self.freq.shape:
            error_s = f"""All parameters must be the same length.
                        {self.gain.shape=}\t{self.freq.shape=}\t{self.noise.shape=}
                      """
            raise ValueError(error_s)
        return self


class RFLineUp(BaseModel):
    """
    class used to size rf line-up
    """

    chain: List[RFBloc]

    def NF(self):
        """
        return the noise figure of the global line-up.
        """
        NF = NoiseFigure(value=list(l.noise.value for l in self.chain))
        gain = PhysicalDimension(
            value=list(l.gain.dB().value for l in self.chain)[:-1], scale="dB"
        )
        return friis(NF, gain)

    def gain(self):
        """
        return the gain of the global line-up.
        """
        gain = np.zeros(self.chain[0].gain.shape)
        for l in self.chain:
            gain += l.gain.dB().value
        print(gain)
        return sum(gain)


def friis(nf: NoiseFigure, gain: PhysicalDimension):
    """

    Parameters
    ----------
    nf : NoiseFigure
        List of the noise figure (in dB) of each block.
    gain : PhysicalDimension
        List of the gain of each block (in dB).


    Returns
    -------
    float
        Total noise figure of the system

    """

    m = gain.shape[0]
    n = nf.shape[0]
    if m != n - 1:
        raise ValueError("gain should have 1 item less than noise factor f")
    g_tot = 1.0
    f_lin = nf.lin()
    res = f_lin[0]
    for i in range(m):
        g_tot *= gain[i].lin()
        res += (f_lin[i + 1] - 1) / g_tot
    return res.dB()
