from setuptools import setup, find_packages

setup(
    name="quant_trade",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "flask-socketio",
        "flask-cors",
        "pandas",
        "numpy",
        "akshare",
    ],
    python_requires=">=3.8",
) 