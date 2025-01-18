from setuptools import setup, find_packages

setup(
    name="giraffe-backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.109.2",
        "uvicorn>=0.27.1",
        "sqlalchemy>=2.0.27",
        "pandas>=2.2.0",
        "numpy>=1.26.4",
        "matplotlib>=3.8.2",
        "seaborn>=0.13.2",
        "python-dotenv>=1.0.1",
        "anthropic>=0.18.1",
        "langchain>=0.1.0",
        "langchain-anthropic>=0.1.0",
        "langchain-core>=0.1.0",
        "pytest>=8.0.1",
        "pytest-asyncio>=0.23.5"
    ],
    python_requires=">=3.9",
) 