from setuptools import setup, find_packages

setup(
    name="quantTrade-aiAgent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'numpy>=1.21.0',
        'pandas>=1.3.0',
        'yfinance>=0.2.0',
        'matplotlib>=3.4.0',
        'seaborn>=0.11.0',
        'plotly>=5.3.0',
        'ta-lib>=0.4.0',
        'pandas-ta>=0.3.0',
        'backtrader>=1.9.76.123',
        'python-dotenv>=0.19.0',
        'tqdm>=4.62.0',
        'pytest>=6.2.5',
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="量化交易个人投资系统",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/lqzhw520/quantTrade-aiAgent",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 