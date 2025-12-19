from hikerservespacecraft.library.sensor_physics import optical_signal_at_distance, luminosity
from hikerverseuniverse.library import constants


def calc_min_absmag_for_lum(luminosity):
    pass


lum = luminosity(constants.R0, 5778)
print(lum)

dd = optical_signal_at_distance(p0=lum, log=False, distance=1 * pc, per_meter=True)

print(dd)



