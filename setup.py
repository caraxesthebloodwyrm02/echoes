from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="automation-framework",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A robust, context-aware Python automation framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/caraxesthebloodwyrm02/echoes",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyYAML>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "automation=automation.scripts.run_automation:main",
        ],
    },
)
