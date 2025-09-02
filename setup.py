from setuptools import setup, find_packages

setup(
    name="kopi-challenge",
    version="1.0.0",
    description="API for a chatbot that always maintains the same stance in debates",
    author="Kopi Challenge Team",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn[standard]",
        "redis",
        "pydantic",
    ],
    python_requires=">=3.11",
)
