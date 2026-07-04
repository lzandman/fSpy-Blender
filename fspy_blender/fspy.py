# fSpy Blender importer
# Copyright (C) 2018 - Per Gantelius
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import json
from struct import *

class ParsingError(Exception):
    pass

class CameraParameters:
  def __init__(self, json_dict):
    if json_dict is None:
        raise ParsingError("Trying to import an fSpy project with no camera parameters")
    principal_point_dict = json_dict["principalPoint"]
    self.principal_point = (principal_point_dict["x"], principal_point_dict["y"])
    self.fov_horiz = json_dict["horizontalFieldOfView"]
    self.camera_transfrom = json_dict["cameraTransform"]["rows"]
    self.image_width = json_dict["imageWidth"]
    self.image_height = json_dict["imageHeight"]

class Project:
  def __init__(self, project_path):
    with open(project_path, "rb") as project_file:
        # The header consists of four little endian uint32s:
        # file id, project version, state string size and image buffer size.
        header = project_file.read(16)
        if len(header) < 16:
            raise ParsingError("Trying to import a file that is not an fSpy project")
        file_id, self.project_version, state_string_size, image_buffer_size = unpack('<IIII', header)

        if 2037412710 != file_id:
            raise ParsingError("Trying to import a file that is not an fSpy project")
        if self.project_version != 1:
            raise ParsingError("Unsupported fSpy project file version " + str(self.project_version))
        if image_buffer_size == 0:
            raise ParsingError("Trying to import an fSpy project with no image data")

        try:
            state = json.loads(project_file.read(state_string_size).decode('utf-8'))
        except (ValueError, UnicodeDecodeError) as e:
            raise ParsingError("Could not parse the fSpy project data: " + str(e))

        try:
            self.camera_parameters = CameraParameters(state["cameraParameters"])
            calibration_settings = state["calibrationSettingsBase"]
            self.reference_distance_unit = calibration_settings["referenceDistanceUnit"]
        except KeyError as e:
            raise ParsingError("The fSpy project is missing expected data: " + str(e))

        self.image_data = project_file.read(image_buffer_size)

    self.file_name = os.path.basename(project_path)