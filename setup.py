import pathlib

from setuptools import setup

NAME = __import__("nextinspace").__name__
VERSION = __import__("nextinspace").__version__
DESCRIPTION = __import__("nextinspace").__description__
URL = "https://github.com/The-Kid-Gid/nextinspace"
AUTHOR = "The-Kid-Gid"
AUTHOR_EMAIL = "gideonshaked@gmail.com"
LICENSE = "GPLv3"

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type="text/markdown",
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    classifiers=[
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Natural Language :: English",
    ],
    packages=["nextinspace"],
    include_package_data=True,
    install_requires=["requests>=2.24.0", "tzlocal>=2.1", "colorama>=0.4.3"],
    entry_points={
        "console_scripts": [
            "nextinspace=nextinspace.__main__:main",
        ]
    },
)
