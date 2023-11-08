"""
The module is dedicated to the handling of accessing non python file resources from within the package.
"""
import importlib.resources
import os
import platform
from pathlib import Path

from open_vp_cal.core import constants


class ResourceLoader:
    """ Class which provides access to the resources which are stored in the resources
     folder within the installed package.

    """
    @staticmethod
    def _get_resource(filename: str) -> str:
        """ For the given filename, we return the absolute file path from within the installed package.

        Args:
            filename: the file name to get the absolute path for

        Returns: The absolute path to the file within the resources folder

        """
        with importlib.resources.path(
                "open_vp_cal.resources", filename
        ) as config_path:
            return str(config_path)

    @classmethod
    def ocio_config_path(cls) -> str:
        """

        Returns: The absolute path to the ocio config file

        """
        return cls._get_resource("studio-config-v1.0.0_aces-v1.3_ocio-v2.1.ocio")

    @classmethod
    def open_vp_cal_logo(cls) -> str:
        """

        Returns: The absolute path to the OpenVP Cal logo

        """
        return cls._get_resource("OpenVPCal_Logo.png")

    @classmethod
    def open_vp_cal_logo_full(cls) -> str:
        """

        Returns: The absolute path to the OpenVP Cal logo full

        """
        return cls._get_resource("OpenVpCal_Full_Logo.png")

    @classmethod
    def slate(cls) -> str:
        """

        Returns: The absolute path to the slate image

        """
        return cls._get_resource("Slate.exr")

    @classmethod
    def regular_font(cls) -> str:
        """

        Returns: The absolute path to the regular font

        """
        return cls._get_resource("Roboto-Regular.ttf")

    @classmethod
    def bold_font(cls) -> str:
        """

        Returns: The absolute path to the bold font

        """
        return cls._get_resource("Roboto-Bold.ttf")

    @classmethod
    def netflix_logo(cls) -> str:
        """

        Returns: The absolute path to the Netflix logo

        """
        return cls._get_resource("Netflix_Logo_RGB.png")

    @classmethod
    def orca_logo(cls) -> str:
        """

        Returns: The absolute path to the Orca logo

        """
        return cls._get_resource("Orca.png")

    @classmethod
    def icon(cls) -> str:
        """

        Returns: The absolute path to the open vp cal icon

        """
        return cls._get_resource("icon.ico")

    @classmethod
    def copy_icon(cls) -> str:
        """

        Returns: The absolute path to the copy icon

        """
        return cls._get_resource("content-copy-custom.png")

    @classmethod
    def default_layout(cls) -> str:
        """

        Returns: The absolute path to the default layout

        """
        if platform.system() == 'Windows':
            return cls._get_resource(constants.UILayouts.DEFAULT_LAYOUT_WINDOWS)
        return cls._get_resource(constants.UILayouts.DEFAULT_LAYOUT)

    @classmethod
    def analysis_layout(cls) -> str:
        """

        Returns: The absolute path to the analysis layout

        """
        if platform.system() == 'Windows':
            return cls._get_resource(constants.UILayouts.ANALYSIS_LAYOUT_WINDOWS)
        return cls._get_resource(constants.UILayouts.ANALYSIS_LAYOUT)

    @classmethod
    def cie_spectrum_bg(cls) -> str:
        """

        Returns: The absolute path to the cie_spectrum_bg image

        """
        return cls._get_resource("cie_spectrum_bg.png")

    @classmethod
    def home_dir(cls) -> Path:
        """ Gets the home directory for the application which lives inside the users home dir

        Returns: The home directory for the application

        """
        home_dir = Path.home() / "OpenVPCal"
        if not os.path.exists(str(home_dir)):
            os.makedirs(home_dir)
        return home_dir

    @classmethod
    def prefs_dir(cls) -> Path:
        """ Gets the preferences directory for the application which lives inside the users home dir

        Returns: The preferences directory for the application

        """
        prefs_dir = cls.home_dir() / "prefs"
        if not os.path.exists(str(prefs_dir)):
            os.makedirs(prefs_dir)
        return prefs_dir

    @classmethod
    def log_dir(cls) -> Path:
        """ Gets the log directory for the application which lives inside the users home dir

        Returns: The log directory for the application

        """
        log_dir = cls.home_dir() / "logs"
        if not os.path.exists(str(log_dir)):
            os.makedirs(log_dir)
        return log_dir

    @classmethod
    def logging(cls) -> str:
        """

        Returns: The logging resource

        """
        return cls._get_resource("logging.bin")