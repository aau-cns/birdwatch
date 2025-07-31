from setuptools import setup, find_packages

setup(
    name="birdwatch",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "customtkinter",
        "from_root",
        "numpy",
        "paramiko",
        "Pillow",
        "PyYAML",
        "setuptools",
        "typing_extensions",
        "psutil"
    ],
    entry_points={
        "console_scripts": [
            "birdwatch=app:main",
            "birdwatchCli=cli:main",
        ],
    },
    python_requires=">=3.6",
)
