from setuptools import setup
import pathlib


# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="nextinspace",
    version=__import__("nextinspace").__version__,
    description="Retrieve the latest from space!",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/The-Kid-Gid/nextinspace",
    author="The-Kid-Gid",
    author_email="gideonshaked@gmail.com",
    license="GPLv3",
    classifiers=[
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Natural Language :: English",
    ],
    packages=["nextinspace"],
    include_package_data=True,
    install_requires=["requests>=2.24.0", "tzlocal>=2.1"],
    entry_points={
        "console_scripts": [
            "nextinspace=nextinspace.__main__:main",
        ]
    },
)
