from setuptools import setup, find_packages

setup(
    name="Echoes",
    version="1.0.0",
    packages=find_packages(),
    description="Advanced AI research platform component of Atmosphere",
    author="Atmosphere Team",
    author_email="team@atmosphere.ai",
    install_requires=[
        "pytest",
        "pytest-asyncio",
        "coverage",
        "requests",
    ],
    python_requires=">=3.8",
)
