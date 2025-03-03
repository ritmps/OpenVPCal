"""
Copyright 2024 Netflix Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Module contains utility functions specific to OpenColorIO
"""
import os
from typing import Any

import PyOpenColorIO as ocio
import pkg_resources
import numpy as np

from colour.models import eotf_ST2084, eotf_inverse_ST2084

from open_vp_cal.core import constants, utils
from open_vp_cal.core.calibrate import resample_lut

# Currently we have a hard requirement on OCIO 2.1+ to support gamut compression
if not pkg_resources.parse_version(ocio.__version__) >= pkg_resources.parse_version(
        "2.1"
):
    raise ImportError("Requires OCIO v2.1 or greater.")


def write_eotf_lut_pq(lut_r, lut_g, lut_b, filename) -> None:
    """ Write a LUT to a file in CLF format using PQ

    Args:
        lut_r: The values for the red channel of the LUT
        lut_g: The values for the green channel of the LUT
        lut_b: The values for the blue channel of the LUT
        filename: The filename to write the LUT to
        peak_lum: The peak luminance of the display in nits
        avoid_clipping: Whether to avoid clipping the LUT values ensuring we do not go beyond the peak luminance
    """
    lut_transform = ocio.Lut1DTransform(length=constants.LUT_LEN, inputHalfDomain=False)

    # resample the lut data to be linearly indexed in PQ where 1 is 100 nits
    value_pq = np.linspace(0, 1, constants.LUT_LEN)
    pq_max_scaled_1_100 = constants.PQ.PQ_MAX_NITS * 0.01

    value = eotf_ST2084(value_pq) / pq_max_scaled_1_100

    lut_r_i = resample_lut(lut_r, value)
    lut_g_i = resample_lut(lut_g, value)
    lut_b_i = resample_lut(lut_b, value)

    lut_r_i_pq = eotf_inverse_ST2084(lut_r_i * pq_max_scaled_1_100)
    lut_g_i_pq = eotf_inverse_ST2084(lut_g_i * pq_max_scaled_1_100)
    lut_b_i_pq = eotf_inverse_ST2084(lut_b_i * pq_max_scaled_1_100)

    for i in range(constants.LUT_LEN):
        lut_transform.setValue(i, lut_r_i_pq[i][0], lut_g_i_pq[i][0], lut_b_i_pq[i][0])

    # write the LUT to CLF format
    write_lut_to_clf(filename, lut_transform)


def write_lut_to_clf(filename: str, lut_transform: ocio.Lut1DTransform) -> None:
    """ Writes the given lut transform to a CLF file for the given filepath

    Args:
        filename: The filename to write the LUT to
        lut_transform: The LUT transform to write
    """
    config = ocio.Config.CreateRaw()
    group = ocio.GroupTransform()
    group.appendTransform(lut_transform)
    with open(filename, "w", encoding="utf-8") as file:
        file.write(group.write(constants.FILE_FORMAT_CLF, config))


def numpy_matrix_to_ocio_matrix(np_mat: np.ndarray) -> Any:
    """ Convert a numpy matrix to an OCIO matrix

    Args:
        np_mat: The numpy matrix to convert

    Returns: The OCIO matrix as a flattened list

    """
    ocio_matrix = np.identity(4)
    ocio_matrix[0:3, 0:3] = np_mat
    return ocio_matrix.flatten().tolist()


def create_EOTF_LUT(lut_filename: str, results: dict) -> ocio.GroupTransform:
    """ Create an EOTF LUT

    Args:
        lut_filename: The filename to write the LUT too
        results: The results from the calibration

    Returns: The OCIO group transform for the EOTF LUT

    """
    # EOTF LUT
    # must be written to a sidecar file, which is named from the config
    write_eotf_lut_pq(
        results[constants.Results.EOTF_LUT_R],
        results[constants.Results.EOTF_LUT_G],
        results[constants.Results.EOTF_LUT_B],
        lut_filename
    )
    eotf_lut = ocio.FileTransform(
        os.path.basename(lut_filename),
        direction=ocio.TransformDirection.TRANSFORM_DIR_INVERSE,
    )
    eotf_lut_group = ocio.GroupTransform()
    # OCIO PQ builtin expects 1 to be 100nits
    eotf_lut_group.appendTransform(ocio.BuiltinTransform("CURVE - LINEAR_to_ST-2084"))
    eotf_lut_group.appendTransform(eotf_lut)
    eotf_lut_group.appendTransform(ocio.BuiltinTransform("CURVE - ST-2084_to_LINEAR"))

    return eotf_lut_group


def create_gamut_compression(results: dict) -> ocio.GroupTransform:
    """ Create a gamut compression transform

    Args:
        results: The results from the calibration

    Returns: The OCIO group transform for the gamut compression

    """
    gamut_comp_group = ocio.GroupTransform()

    # the three distances (called limits in the ctl) that we'll modify.
    max_dists = results[constants.Results.MAX_DISTANCES]

    lim_cyan = utils.clamp(
        max_dists[0], constants.GAMUT_COMPRESSION_LIMIT_MIN, constants.GAMUT_COMPRESSION_LIMIT_MAX)
    lim_magenta = utils.clamp(
        max_dists[1], constants.GAMUT_COMPRESSION_LIMIT_MIN, constants.GAMUT_COMPRESSION_LIMIT_MAX)
    lim_yellow = utils.clamp(
        max_dists[2], constants.GAMUT_COMPRESSION_LIMIT_MIN, constants.GAMUT_COMPRESSION_LIMIT_MAX)

    # other values shouldn't need to change, so hard coding.
    gc_params = [lim_cyan, lim_magenta, lim_yellow, 0.9, 0.9, 0.9, 4.0]

    # ACES gamut comp incorporates AP0 to AP1 input transform, which we need
    # to counteract by applying an AP1 to AP0 pre-transform and AP0 to AP1
    # post-transform
    gamut_comp_group.appendTransform(ocio.BuiltinTransform("ACEScg_to_ACES2065-1"))

    gamut_comp_group.appendTransform(
        ocio.FixedFunctionTransform(
            ocio.FixedFunctionStyle.FIXED_FUNCTION_ACES_GAMUT_COMP_13, gc_params
        )
    )

    gamut_comp_group.appendTransform(
        ocio.BuiltinTransform(
            "ACEScg_to_ACES2065-1", ocio.TransformDirection.TRANSFORM_DIR_INVERSE
        )
    )

    return gamut_comp_group


def populate_ocio_group_transform_for_CO_CS_EOTF(
        clf_name: str, group: ocio.GroupTransform, output_folder: str, results: dict) -> None:
    """ Populate the OCIO group transform for the CO_CS_EOTF calculation order

    Args:
        clf_name: The name of the clf file we want to write out
        group: The OCIO group transform to add the transforms to
        output_folder: The folder to write the CLF files to
        results: The results from the calibration

    """
    # EOTF LUT
    if results[constants.Results.ENABLE_EOTF_CORRECTION]:
        clf_name = os.path.join(output_folder, clf_name + ".clf")
        eotf_lut_group = create_EOTF_LUT(clf_name, results)
        group.appendTransform(eotf_lut_group)

    # matrix transform to screen colour space
    group.appendTransform(
        ocio.MatrixTransform(
            numpy_matrix_to_ocio_matrix(results[constants.Results.TARGET_TO_SCREEN_MATRIX])
        )
    )


def populate_ocio_group_transform_for_CO_EOTF_CS(
        clf_name: str, group: ocio.GroupTransform, output_folder: str, results: dict) -> None:
    """ Populate the OCIO group transform for the CO_EOTF_CS calculation order

    Args:
        clf_name: The name of the clf file we want to write out
        group: The OCIO group transform to add the transforms to
        output_folder: The folder to write the CLF files to
        results: The results from the calibration
    """
    group.appendTransform(
        ocio.MatrixTransform(
            numpy_matrix_to_ocio_matrix(results[constants.Results.TARGET_TO_SCREEN_MATRIX])
        )
    )

    # EOTF LUT
    # must be written to a sidecar file, which is named from the config
    if results[constants.Results.ENABLE_EOTF_CORRECTION]:
        lut_filename = os.path.join(output_folder, clf_name + ".clf")
        eotf_lut_group = create_EOTF_LUT(lut_filename, results)
        group.appendTransform(eotf_lut_group)


def bake_3d_lut(
        input_color_space: str, ocio_display_colour_space: str, ocio_view_transform: str, config_path: str,
        output_lut_path: str, cube_size: int = 64, lut_format: str = "resolve_cube") -> str:
    """
    Bake a 3D LUT from an OpenColorIO configuration.

    Args:
        input_color_space (str): The input colour space.
        ocio_display_colour_space (str): The OCIO display colour space.
        ocio_view_transform (str): The OCIO view transform.
        config_path (str): Path to the OCIO configuration file.
        output_lut_path (str): Path to save the baked 3D LUT.
        cube_size (int): Cube size for the 3D LUT. Default is 33.
        lut_format (str): Format for the 3D LUT. Default is "cub".
    """
    # Load the OCIO configuration
    config = ocio.Config.CreateFromFile(config_path)

    # Validate the colour spaces
    if not any(cs.getName() == input_color_space for cs in config.getColorSpaces()):
        raise ValueError(f"Input color space '{input_color_space}' does not exist in the provided OCIO config.")

    if not any(cs == ocio_display_colour_space for cs in config.getDisplaysAll()):
        raise ValueError(
            f"Display Colour Space '{ocio_display_colour_space}' does not exist in the provided OCIO config.")

    if not any(cs == ocio_view_transform for cs in config.getViews(ocio_display_colour_space)):
        raise ValueError(
            f"View Transform '{ocio_view_transform}' does not exist in the provided OCIO config.")

    # Create the Baker and set its properties
    baker = ocio.Baker()
    baker.setConfig(config)
    baker.setFormat(lut_format)
    baker.setInputSpace(input_color_space)
    baker.setDisplayView(ocio_display_colour_space, ocio_view_transform)
    baker.setCubeSize(cube_size)

    # Bake the LUT
    baker.bake(output_lut_path)
    return output_lut_path
