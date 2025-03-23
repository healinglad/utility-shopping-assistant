#!/usr/bin/env python3
"""
Setup script for the Shopping Assistant package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="shopping-assistant",
    version="0.1.0",
    author="Shopping Assistant Team",
    author_email="example@example.com",
    description="A utility to help users find the best products to buy based on their inputs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/shopping-assistant",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "shopping-assistant=shopping_assistant.main:main",
            "shopping-assistant-web=shopping_assistant.web_interface:main",
        ],
    },
    include_package_data=True,
)
