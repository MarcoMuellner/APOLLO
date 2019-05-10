from uncertainties.umath import *
from uncertainties import ufloat
import numpy as np

P_mass     = [ 0.97531880, -1.43472745,  1.21647950]
P_radius   = [ 0.30490057, -1.12949647,  0.31236570]

class ScalingRelations:
    def __init__(self, nu_max, delta_nu, t_eff):
        #Values from Bellinger 2018
        self._t_sun = ufloat(5772,0.8)
        self._nu_max_sun = ufloat(3090,30)
        self._logg_sun = 4.44
        self._delta_nu_sun = ufloat(135.1,0.1)

        self._nu_max = nu_max
        self._delta_nu = delta_nu
        self._t_eff = t_eff

        self._log_g = self._logg_sun + log10((nu_max / self._nu_max_sun) * sqrt(t_eff / self._t_sun))

        # return (10 ** log_g / 10 ** logg_sun) * 1 / np.sqrt(10 ** log_t_eff / t_sun) * nu_max_sun
        pass

    def scaling_relation(self, alpha, beta, gamma):
        try:
            return pow((self._nu_max / self._nu_max_sun), alpha) * pow((self._delta_nu / self._delta_nu_sun), beta) * pow(
                (self._t_eff / self._t_sun), gamma)
        except:
            return np.nan

    def radius(self):
        return self.scaling_relation(*P_radius)

    def log_g(self):
        return self._logg_sun + log10((self._nu_max / self._nu_max_sun) * sqrt(self._t_eff / self._t_sun))

    def mass(self):
        return self.scaling_relation(*P_mass)
