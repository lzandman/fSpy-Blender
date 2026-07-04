# Builds a distributable extension zip.
#
# The officially supported way to package a Blender extension is
#
#     blender --command extension build
#
# run from inside the fspy_blender directory. This script reproduces the same
# result without requiring a Blender executable on PATH: it bundles the
# manifest and the Python sources at the root of the zip, which is the layout
# the extensions platform expects.

import glob
import os
import re
import zipfile

src_dir_name = 'fspy_blender'
manifest_path = os.path.join(src_dir_name, 'blender_manifest.toml')

# Extract the version string from the manifest
version = None
with open(manifest_path) as manifest_file:
    for line in manifest_file:
        match = re.match(r'\s*version\s*=\s*"([^"]+)"', line)
        if match:
            version = match.group(1)
            break

if version is None:
    raise RuntimeError("Could not extract version number from " + manifest_path)

dist_dir_name = "dist"
os.makedirs(dist_dir_name, exist_ok=True)

dist_archive_name = "fSpy-Blender-" + version + ".zip"

with zipfile.ZipFile(
    os.path.join(dist_dir_name, dist_archive_name),
    'w',
    zipfile.ZIP_DEFLATED
) as zipf:
    # The manifest and Python files must sit at the root of the extension zip
    zipf.write(manifest_path, os.path.basename(manifest_path))
    for py_file in sorted(glob.glob(os.path.join(src_dir_name, '*.py'))):
        zipf.write(py_file, os.path.basename(py_file))

print("Wrote " + os.path.join(dist_dir_name, dist_archive_name))
