from distutils.core import setup

import os

def make_package_name(path):
    s = path.replace("./", "").replace("/", ".")
    return s

packages = []

for (path, directories, filenames) in os.walk('.'):
    if "__init__.py" in filenames:
        packages.append(make_package_name(path))



setup(
    name="blacklynx-aerospace",
    version="0.0.1",
    packages=packages,
    include_package_data=True,
    license='Blacklynx Proprietary')