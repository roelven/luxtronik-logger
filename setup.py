from setuptools import setup, find_packages

setup(
    name="lux-logger",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0",
        "apscheduler>=3.9",
    ],
    dependency_links=[
        "git+https://github.com/Bouni/python-luxtronik.git#egg=python-luxtronik",
    ],
    python_requires=">=3.10",
)