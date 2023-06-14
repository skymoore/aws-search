#!/usr/bin/env python3

import os, sys
from setuptools import find_packages, setup


def read(*parts):
    """Read file."""
    filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), *parts)
    sys.stdout.write(filename)
    with open(filename, encoding="utf-8", mode="rt") as fp:
        return fp.read()


with open("./README.md") as readme_file:
    readme = readme_file.read()

setup(
    author="Sky Moore",
    author_email="i@msky.me",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.10",
    ],
    description="AWS Multi Region Concurrent Query Tool",
    include_package_data=True,
    keywords=["aws", "multi-region"],
    license="MIT",
    long_description_content_type="text/markdown",
    long_description=readme,
    name="aws-multi-region-search",
    packages=find_packages(include=["awss"]),
    entry_points={"console_scripts": ["awss = awss.__main__:cli"]},
    url="https://github.com/skymoore/aws-search",
    version="v0.0.1",
    zip_safe=True,
)
