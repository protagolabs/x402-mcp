from setuptools import setup, find_packages

setup(
    name="x402-mcp",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastmcp",
        "x402",
        "cdp-sdk"
    ],
    entry_points={
        "console_scripts": [
            "x402-mcp=x402_mcp.app:main",
        ],
    },
    python_requires=">=3.12",
)
