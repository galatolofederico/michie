import setuptools
import os

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "README.md"), "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="michie",
    version="0.2",
    author="Federico A. Galatolo",
    author_email="federico.galatolo@ing.unipi.it",
    description="",
    url="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        "tqdm>=4.64.1",
        "pygame>=2.1.2",
        "numpy>=1.23.4",
        "schema>=0.7.5",
        "scipy>=1.9.2",
        "orjson>=3.8.0",
        "lru-dict==1.1.8"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Intended Audience :: Science/Research",
        "Development Status :: 4 - Beta"
    ],
)