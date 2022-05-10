import setuptools
import pathlib

with open("docs/README.md", "r") as fh:
    long_description = fh.read()

HERE = pathlib.Path(__file__).parent
INSTALL_REQUIRES = (HERE / "requirements.txt").read_text().splitlines()

setuptools.setup(
    name="passive-auto-design",
    version="0.1.8",
    author="Patarimi",
    author_email="mpqqch@gmail.com",
    description="Tools for fast prototyping of radio-frequence passive components",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Patarimi/PassiveAutoDesign",
    packages=setuptools.find_packages(),
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
