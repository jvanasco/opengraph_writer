"""opengraph_writer installation script.
"""
import os
import re

from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.md")).read()
README = README.split("\n\n", 1)[0] + "\n"

# store version in the init.py
with open(os.path.join(os.path.dirname(__file__),
                       'opengraph_writer',
                       '__init__.py'
                       )
          ) as v_file:
    VERSION = re.compile(
        r".*__VERSION__ = '(.*?)'",
        re.S).match(v_file.read()).group(1)

requires = [
    "metadata_utils >=0.1.1",
    'six',
]

setup(
    name="opengraph_writer",
    description="Lightweight open graph support for writing and validating objects",
    version=VERSION,
    url="https://github.com/jvanasco/opengraph_writer",
    author="Jonathan Vanasco",
    author_email="jonathan@findmeon.com",
    long_description=README,
    zip_safe=False,
    keywords="web pyramid facebook opengraph open graph",
    tests_require = requires,
    install_requires = requires,
    test_suite='tests',
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
