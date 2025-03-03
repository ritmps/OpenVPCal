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

This module contains utility functions for the framework
"""
import base64
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Union, TYPE_CHECKING, List, Tuple

from open_vp_cal.core import constants, ocio_config
from open_vp_cal.core.ocio_config import OcioConfigWriter
from open_vp_cal.core.resource_loader import ResourceLoader
from open_vp_cal.framework.generation import PatchGeneration

if TYPE_CHECKING:
    from open_vp_cal.led_wall_settings import LedWallSettings
    from open_vp_cal.project_settings import ProjectSettings


def generate_patterns_for_led_walls(project_settings: 'ProjectSettings', led_walls: List['LedWallSettings']) -> str:
    """ For the given list of led walls filter out any walls which are verification walls, then generate the
        calibration patterns for the remaining walls.

    Args:
        project_settings: The project settings with the settings for the pattern generation
        led_walls: A list of led walls we want to generate patters for

    Returns: The ocio config file path which was generated

    """
    led_walls = [led_wall for led_wall in led_walls if not led_wall.is_verification_wall]
    if not led_walls:
        return ""

    for led_wall in led_walls:
        patch_generator = PatchGeneration(led_wall)
        patch_generator.generate_patches(constants.PATCHES.PATCH_ORDER)

    _, ocio_config_path = export_pre_calibration_ocio_config(project_settings, led_walls)
    return ocio_config_path


def export_pre_calibration_ocio_config(
        project_settings: 'ProjectSettings',
        led_walls: List['LedWallSettings']) -> tuple[OcioConfigWriter, str]:
    """ Export the pre calibration ocio config file for the given walls and project settings

    """
    config_writer = ocio_config.OcioConfigWriter(project_settings.export_folder)
    return config_writer, config_writer.generate_pre_calibration_ocio_config(led_walls)
