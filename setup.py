"""opengraph_writer installation script.
"""
import os
import re

from setuptools import setup
from setuptools import find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

long_description = (
    description
) = "Lightweight OpenGraph support for writing and validating objects."
with open(os.path.join(HERE, "README.md")) as r_file:
    long_description = r_file.read()

# store version in the init.py
with open(os.path.join(HERE, "opengraph_writer", "__init__.py")) as v_file:
    VERSION = re.compile(r'.*__VERSION__ = "(.*?)"', re.S).match(v_file.read()).group(1)

requires = [
    "metadata_utils>=0.1.1",
    "six",
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
    zip_safe=False,
    keywords="facebook opengraph open graph web pyramid",
    install_requires=requires,
    tests_require=requires,
    extras_require={
        "testing": testing_extras,
    },
    test_suite="tests",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Developers",
        "Framework :: Pyramid",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    license="MIT",
)
