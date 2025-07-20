# Update setup.py
from setuptools import setup, find_packages

setup(
    name="zombicide-simulation",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pygame>=2.5.0",
        "pytest>=7.3.1",
        "pyyaml>=6.0.1",
    ],
    entry_points={
        'console_scripts': [
            'zombicide=zombicide.main:main',
        ],
    },
)