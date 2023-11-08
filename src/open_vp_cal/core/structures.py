"""
This module contains the structures for containing data which run through the framework
"""
from open_vp_cal.core.constants import ValidationStatus


class ProcessingResults:
    """ Class to store the results of the processing

    """
    def __init__(self):
        self.samples = None
        self.reference_samples = None
        self.sample_buffers = []
        self.sample_buffers_stitched = None
        self.sample_reference_buffers = []
        self.sample_reference_buffers_stitched = None
        self.sample_swatch_nested = None
        self.pre_calibration_results = None
        self.calibration_results = None
        self.ocio_config_output_file = None
        self.calibration_results_file = None
        self.lut_output_file = None
        self.led_wall_colour_spaces = None



class ValidationResult:
    """ Small class to hold the results of the validation check

    """
    name = ""
    status = ValidationStatus.PASS
    message = ""


class SamplePatchResults:
    """
    Class to store the results of patch sampling.
    """

    def __init__(self):
        """
        Initialize an instance of SamplePatchResults.
        """
        self.samples = []
        self.frames = []


class ConfigurationResult:
    """ Simple class to hold the results of the configuration check
    """
    param = ""
    value = ""


class LedWallColourSpaces:
    """
    Simple class to store all the colour spaces for a led wall
    """
    calibration_cs = None
    calibration_preview_cs = None
    target_with_inv_eotf_cs = None
    target_gamut_cs = None
    view_transform = None
    pre_calibration_view_transform = None
    display_colour_space_cs = None
    aces_to_cie_d65_cat02_cs = None
    transfer_function_only_cs = None