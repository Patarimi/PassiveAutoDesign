from pydantic import FilePath
from matplotlib.ticker import EngFormatter
import klayout.db as db
from .lumped_element import LumpedElement
from ..units.constants import u0

Ind = EngFormatter(unit="H")


class Inductor(LumpedElement):
    """
    class describing a inductor behavior using wheeler formula for ic
    """

    def __init__(self, d_i=100e-6, n_turn=1, width=3e-6, gap=1e-6, k_1=2.25, k_2=3.55):
        param = {"d_i": d_i, "n_turn": n_turn, "width": width, "gap": gap}
        const = {"k_1": k_1, "k_2": k_2}
        LumpedElement.__init__(self, dim=param, const=const)

    def __str__(self):
        return Ind(self.model["ind"])

    def get_model(self):
        n = self.dim["n_turn"]
        outer_diam = (
                self.dim["d_i"] + 2 * n * self.dim["width"] + 2 * (n - 1) * self.dim["gap"]
        )
        self.dim["d_o"] = outer_diam
        rho = (self.dim["d_i"] + outer_diam) / 2
        density = (outer_diam - self.dim["d_i"]) / (outer_diam + self.dim["d_i"])
        ind = self.const["k_1"] * u0 * n ** 2 * rho / (1 + self.const["k_2"] * density)
        return {"ind": ind}

    def draw(self, file: FilePath):
        ly = db.Layout()

        # sets the database unit to 1 nm
        ly.dbu = 0.001

        # adds a single top cell
        top_cell = ly.create_cell("inductor")

        # creates a new layer (layer number 1, datatype 0)
        layer1 = ly.layer(1, 0)
        d_i = 5.0
        pts = [db.DPoint(0, -d_i/2),
               db.DPoint(d_i/2, -d_i / 2),
               db.DPoint(d_i/2, d_i / 2),
               db.DPoint(0, d_i / 2),
               ]
        rect = db.DPath(pts, 2.0)
        top_cell.shapes(layer1).insert(rect)

        ly.write(file)
