import math
#
import numpy as np

from hikerservespacecraft.payloads.sensors import PowerLawSignalPropagationModel

from hikerservespacecraft.library import unit
from hikerverseuniverse.library import constants, celestial_constants

ten_pc = 10.0 * unit.pc

subspace_propagation_expoenent = 1.01

LUMINOSITY_FACTOR = 0.4
ABSOLUTE_MAGNITUDE_STD = 4.85



redco = [1.62098281e-82, -5.03110845e-77, 6.66758278e-72, -4.71441850e-67, 1.66429493e-62, -1.50701672e-59,
         -2.42533006e-53, 8.42586475e-49, 7.94816523e-45, -1.68655179e-39, 7.25404556e-35, -1.85559350e-30,
         3.23793430e-26, -4.00670131e-22, 3.53445102e-18, -2.19200432e-14, 9.27939743e-11, -2.56131914e-07,
         4.29917840e-04, -3.88866019e-01, 3.97307766e+02]
greenco = [1.21775217e-82, -3.79265302e-77, 5.04300808e-72, -3.57741292e-67, 1.26763387e-62, -1.28724846e-59,
           -1.84618419e-53, 6.43113038e-49, 6.05135293e-45, -1.28642374e-39, 5.52273817e-35, -1.40682723e-30,
           2.43659251e-26, -2.97762151e-22, 2.57295370e-18, -1.54137817e-14, 6.14141996e-11, -1.50922703e-07,
           1.90667190e-04, -1.23973583e-02, -1.33464366e+01]
blueco = [2.17374683e-82, -6.82574350e-77, 9.17262316e-72, -6.60390151e-67, 2.40324203e-62, -5.77694976e-59,
          -3.42234361e-53, 1.26662864e-48, 8.75794575e-45, -2.45089758e-39, 1.10698770e-34, -2.95752654e-30,
          5.41656027e-26, -7.10396545e-22, 6.74083578e-18, -4.59335728e-14, 2.20051751e-10, -7.14068799e-07,
          1.46622559e-03, -1.60740964e+00, 6.85200095e+02]

redco = np.poly1d(redco)
greenco = np.poly1d(greenco)
blueco = np.poly1d(blueco)


def temp2rgb(temp):
    red = redco(temp)
    green = greenco(temp)
    blue = blueco(temp)

    if red > 255:
        red = 255
    elif red < 0:
        red = 0
    if green > 255:
        green = 255
    elif green < 0:
        green = 0
    if blue > 255:
        blue = 255
    elif blue < 0:
        blue = 0

    color = (int(red),
             int(green),
             int(blue))
    print(color)
    return color


def bv_to_temp_kelvin(bv):
    return 4600.0 * ((1.0 / ((0.92 * bv) + 1.7)) + (1.0 / ((0.92 * bv) + 0.62)))


def temp_kelvin_to_bv(t):
    a = (0.8464 * t)
    b = (2.1344 * t) - 8464.0
    c = (1.0540 * t) - 10672.0
    D = (b * b) - (4.0 * a * c)
    if D < 0.0:
        D = 0.0
    else:
        D = math.sqrt(D)
    return (-b + D) / (2.0 * a)



def lum(R, T):
    L = 4*math.pi*math.pow(R, 2) * constants.sigmaSB*math.pow(T, 4)



def star_radius_in_m(temp_in_kelvin, luminosity_in_watts):
    return math.sqrt(luminosity_in_watts / (4 * math.pi * constants.sigmaSB * math.pow(temp_in_kelvin, 4)))


def subspace_signal_dispersion_to_distance(signal_dispersion: float) -> float:
    """
    :param signal_dispersion: The signal dispersion value in the subspace
    :return: The distance calculated from the signal dispersion
    """
    return math.sqrt(signal_dispersion) * ten_pc


def distance_to_subspace_signal_dispersion(distance):
    index = 2.0
    return math.pow(distance / ten_pc, index)


def dbm_to_watts(power_dbm):
    return db_to_watts(power_dbm - 30)


def db_to_watts(power_db: float) -> float:
    """
    :param power_db: The power level in dB
    :return: The equivalent power level in watts
    """
    return 1 * math.pow(10, power_db / 10.0)


def watts_to_db(power_watts):
    return 10 * math.log10(power_watts / 1.0)


def watts_to_dbm(power_watts):
    return watts_to_db(power_watts) + 30



# Stellar magnitudes and luminosity
def abs_mag_2_luminosity_in_lg(abs_mag):
    return math.pow(10, (-LUMINOSITY_FACTOR) * (abs_mag - ABSOLUTE_MAGNITUDE_STD))


def abs_mag_2_luminosity_in_w(abs_mag):
    return math.pow(10, (-LUMINOSITY_FACTOR) * (abs_mag - ABSOLUTE_MAGNITUDE_STD)) * celestial_constants.G2V_STAR_LUMINOSITY


def luminosity_in_watts_to_absmag(luminosity_watts):
    luminosity_in_lg = luminosity_watts / celestial_constants.G2V_STAR_LUMINOSITY
    return ABSOLUTE_MAGNITUDE_STD - (2.5 * (math.log10(luminosity_in_lg)))


def luminosity_in_lg_to_absmag(luminosity_lg):
    return ABSOLUTE_MAGNITUDE_STD - (2.5 * (math.log10(luminosity_lg)))


def absolute_magnitude_to_apparent_magnitude_at_distance(absmag, distance):
    distance_pc = distance / unit.pc
    distance_modulous = 5.0 * math.log10(distance_pc) - 5.0
    return distance_modulous + absmag


def apparent_magnitude_to_absolute_magnitude(app_mag, distance):
    distance_pc = distance / unit.pc
    distance_modulous = 5.0 * math.log10(distance_pc) - 5.0
    return app_mag - distance_modulous


def optical_signal_at_distance(initial_power: float, is_log_mode: bool, distance: float, is_per_meter: bool):
    surface_area = 1.0
    if is_per_meter:
        surface_area = 4 * math.pi * distance * distance

    power_law = PowerLawSignalPropagationModel(2.0)

    if not is_log_mode:
        return initial_power / surface_area
    else:
        return math.pow(10, power_law.get_signal(math.log10(initial_power), distance)) / surface_area


def optical_signal_at_distance_in_log10(p0, distance):
    power_law = PowerLawSignalPropagationModel(2.0)
    return power_law.get_signal(p0, distance)


# PhysicsDataProvider.RADAR_PROPAGATION_INDEX


def radar_signal_at_distance(p0, distance, per_meter):
    surface_area = 1.0
    if per_meter:
        surface_area = 4 * math.pi * distance * distance

    power_law = PowerLawSignalPropagationModel(2.0)
    return math.pow(10, power_law.get_signal(math.log10(p0), distance)) / surface_area


def radar_signal_at_distance_in_log10(p0, distance):
    power_law = PowerLawSignalPropagationModel(2.0)
    return power_law.get_signal(p0, distance)


def gravimetric_signal_at_distance(p0, distance, per_meter):
    surface_area = 1.0
    if per_meter:
        surface_area = 4 * math.pi * distance * distance

    power_law = PowerLawSignalPropagationModel(2.0)
    return math.pow(10, power_law.get_signal(math.log10(p0), distance)) / surface_area


def gravimetric_signal_at_distance_in_log10(p0, distance):
    power_law = PowerLawSignalPropagationModel(2.0)
    return power_law.get_signal(p0, distance)


def magnetometric_signal_at_distance(p0, distance, per_meter):
    surface_area = 1.0
    if per_meter:
        surface_area = 4 * math.pi * distance * distance

    power_law = PowerLawSignalPropagationModel(2.0)
    return math.pow(10, power_law.get_signal(math.log10(p0), distance)) / surface_area


def magnetometric_signal_at_distance_in_log10(p0, distance):
    power_law = PowerLawSignalPropagationModel(2.0)
    return power_law.get_signal(p0, distance)


def subspace_signal_at_distance(p0, distance, per_meter):
    surface_area = 1.0
    if per_meter:
        surface_area = 4 * math.pi * distance * distance

    power_law = PowerLawSignalPropagationModel(2.0)
    return math.pow(10, power_law.get_signal(math.log10(p0), distance)) / surface_area


def subspace_signal_at_distance_in_log10(p0, distance):
    power_law = PowerLawSignalPropagationModel(2.0)
    return power_law.get_signal(p0, distance)


def photons_to_watts(number_photons, wavelength):
    return number_photons * (constants.c / wavelength) * constants.Planck


def watts_to_photons(photon_power, wavelength):
    return photon_power * wavelength / (constants.c * constants.Planck)


def luminosity(radius, temperature):
    return 4 * math.pi * radius * radius * constants.sigmaSB * temperature * temperature * temperature * temperature
# L*L*W*T*T*T*T / L*L*T*T*T*T


def peak_bb_wavelength(temperature_kelvin):
    return 2.898e-3 / temperature_kelvin


def black_body(temperature_kelvin, wavelength_m):
    return (8.0 * math.pi * constants.Planck * constants.c) / (math.pow(wavelength_m, 5) *
                                                               (math.exp((constants.Planck * constants.c) / (
                                                                       wavelength_m * constants.Kb * temperature_kelvin)) - 1))


def generate_bb_spectrum(temperature_kelvin):
    spectrum = []
    wavelengths = np.power(10, np.linspace(-7, 3, num=1000))
    lams = []

    for lam in wavelengths:
        lams.append(lam)
        spectrum.append(black_body(temperature_kelvin=temperature_kelvin, wavelength_m=lam))

    return lams, spectrum


def spectral_flux_density_per_meter(spectral_magnitude, standard_apparent_magnitudes):
    freq = constants.c / standard_apparent_magnitudes.peakWavelength
    fx0 = standard_apparent_magnitudes.fluxInJy
    fx_fx0 = math.pow(10, -0.4 * spectral_magnitude)
    return fx_fx0 * fx0 * freq


# lum = luminosity(constants.R0, 5778)
# print(lum)
#
# abs_lum = abs_mag_2_luminosity_in_w(abs_mag=4.85)
# print(abs_lum)
#
# peakWavelength = peak_bb_wavelength(5778)
# print(peakWavelength)
#
#
# wavelengths, spectrum = generate_bb_spectrum(5778)
#
# print(spectrum)
#
# import matplotlib.pyplot as plt
# plt.loglog(wavelengths, spectrum, 'k-')
#
# # show the plot
# plt.show()
