"""opengraph_writer installation script.
"""
import os
import re

from setuptools import find_packages
from setuptools import setup

HERE = os.path.abspath(os.path.dirname(__file__))

long_description = (
    description
) = "Lightweight OpenGraph support for writing and validating objects."
with open(os.path.join(HERE, "README.md")) as r_file:
    long_description = r_file.read()

# store version in the init.py
with open(os.path.join(HERE, "src", "opengraph_writer", "__init__.py")) as v_file:
    VERSION = re.compile(r'.*__VERSION__ = "(.*?)"', re.S).match(v_file.read()).group(1)

requires = [
    "metadata_utils>=0.2.0",
]
tests_require = [
    "pytest",
    "pyramid",
]
testing_extras = tests_require + []
setup(
    name="opengraph_writer",
    url="https://github.com/jvanasco/opengraph_writer",
    author="Jonathan Vanasco",
    author_email="jonathan@findmeon.com",
    version=VERSION,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    zip_safe=False,
    python_requires=">=3.6",
    keywords="facebook opengraph open graph web pyramid",
    install_requires=requires,
    tests_require=requires,
    extras_require={
        "testing": testing_extras,
    },
    test_suite="tests",
    packages=find_packages(
        where="src",
    ),
    package_dir={"": "src"},
    package_data={"metadata_utils": ["py.typed"]},
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Developers",
        "Framework :: Pyramid",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
    ],
    license="MIT",
)
