"""
Setup script for MediaScan package.
"""

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mediascan",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Simple JSON Media Database Search",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mediascan",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia",
    ],
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "mediascan=mediascan.cli:main",
        ],
    },
    keywords="media search json movies tv series database",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/mediascan/issues",
        "Source": "https://github.com/yourusername/mediascan",
        "Documentation": "https://mediascan.readthedocs.io/",
    },
)
