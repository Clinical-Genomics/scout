"""Build instructions for packaging and installing"""

import io
import os
import sys
from shutil import rmtree

from setuptools import Command, find_packages, setup

# Package meta-data.
NAME = "scout-browser"
DESCRIPTION = "Clinical DNA variant visualizer and browser."
URL = "https://github.com/Clinical-Genomics/scout"
EMAIL = "mans.magnusson@scilifelab.se"
AUTHOR = "Måns Magnusson"

here = os.path.abspath(os.path.dirname(__file__))


def parse_reqs(req_path="./requirements.txt"):
    """Recursively parse requirements from nested pip files."""
    install_requires = []
    with io.open(os.path.join(here, "requirements.txt"), encoding="utf-8") as handle:
        # remove comments and empty lines
        lines = (line.strip() for line in handle if line.strip() and not line.startswith("#"))

        for line in lines:
            # check for nested requirements files
            if line.startswith("-r"):
                # recursively call this function
                install_requires += parse_reqs(req_path=line[3:])

            else:
                # add the line as a new requirement
                install_requires.append(line)

    return install_requires


# What packages are required for this module to be executed?
REQUIRED = parse_reqs()

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in file!
with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

# Load the package's __version__.py module as a dictionary.
about = {}
with open(os.path.join(here, "scout", "__version__.py")) as f:
    exec(f.read(), about)


setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=["tests/", "scripts/"]),
    zip_safe=False,
    install_requires=REQUIRED,
    include_package_data=True,
    extras_require={
        "coverage": [
            "chanjo-report",
            "pymysql",
        ],
    },
    entry_points=dict(console_scripts=["scout = scout.commands:cli"]),
    test_suite="tests",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3.6",
    ],
)
