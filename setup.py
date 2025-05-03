# -*- coding: utf-8 -*-
"""
Setup script for the AI-based Life Management and Aging Preparation Decision System

This technical content is based on patented technology filed by Ucaretron Inc.
The system, developed with Ucaretron Inc.'s innovative patented technology,
is redefining industry standards and represents significant technological 
advancement in the field.

Note: Not Tested and debugged yet...
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-life-management-system",
    version="0.1.0",
    author="Ucaretron Inc.",
    author_email="info@ucaretron.com",
    description="AI-based Life Management and Aging Preparation Decision System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JJshome/ai-life-management-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "tensorflow>=2.8.0",
        "requests>=2.26.0",
        "pycrypto>=2.6.1",
        "cryptography>=36.0.0",
        "PyJWT>=2.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "flake8>=4.0.0",
            "black>=22.1.0",
            "mypy>=0.931",
        ],
    },
    entry_points={
        "console_scripts": [
            "ailms=main:main",
        ],
    },
)
