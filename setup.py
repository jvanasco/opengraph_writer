"""opengraph_writer installation script.
"""
import os

from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.md")).read()
README = README.split("\n\n", 1)[0] + "\n"

requires = []

setup(\
    name="opengraph_writer",
    description="Lightweight open graph support for writing and validating objects",
    version="0.1.0",
    url="https://github.com/jvanasco/opengraph_writer",
    author="Jonathan Vanasco",
    author_email="jonathan@findmeon.com",
    long_description=README,
    zip_safe=False,
    keywords="web pylons pyramid facebook opengraph open graph",
    test_suite='tests',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Developers",
        "Framework :: Pylons",
        "Framework :: Pyramid",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
    ],
    license="MIT",
)

