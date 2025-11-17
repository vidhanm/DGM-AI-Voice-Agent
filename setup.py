"""Setup script for Darwin Gödel Machine Voice Agent."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')
    requirements = [r.strip() for r in requirements if r.strip() and not r.startswith('#')]

setup(
    name="dgm-voice-agent",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A self-evolving voice agent platform using Darwin-Gödel Machine principles",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/DGM-AI-Voice-Agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "dgm-agent=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
