"""
Setup script for multi-agent-generator package.
"""
from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
try:
    long_description = (HERE / "README.md").read_text(encoding="utf-8")
except FileNotFoundError:
    long_description = "Multi-Agent Generator - Generate multi-agent AI code from natural language"

REQUIREMENTS = [
    "litellm>=0.1.0",
    "streamlit>=1.22.0",
    "langchain>=0.0.271",
    "langchain-core>=0.0.1",
    "langchain-openai>=0.0.1",
    "langgraph>=0.0.16",
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
    "agno==1.8.4",
]

setup(
    name="multi-agent-generator",
    version="0.4.0",
    description="Generate multi-agent AI teams from plain English using LiteLLM-compatible providers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Aakriti Aggarwal",
    author_email="aakritiaggarwal2k@gmail.com",
    url="https://github.com/aakriti1318/multi-agent-generator",
    packages=find_packages(),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    extras_require={
        "watsonx": ["ibm-watsonx-ai>=0.2.0"],
        "dev": ["pytest>=7.0.0", "black>=23.0.0", "flake8>=6.0.0", "twine", "build"],
    },
    entry_points={
        "console_scripts": [
            "multi-agent-generator=multi_agent_generator.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
