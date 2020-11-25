"""Build instructions for packaging and installing"""

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = "scout-browser"
DESCRIPTION = "Clinical DNA variant visualizer and browser."
URL = "https://github.com/Clinical-Genomics/scout"
EMAIL = "mans.magnusson@scilifelab.se"
AUTHOR = "Måns Magnusson"

here = os.path.abspath(os.path.dirname(__file__))


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
    include_package_data=True,
    extras_require=dict(coverage=["chanjo-report"]),
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
