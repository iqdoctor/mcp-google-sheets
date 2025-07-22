from setuptools import setup

setup(
    name="mcp-google-sheets-local",
    version="0.1.0",
    packages=["mcp_google_sheets"],
    install_requires=[
        "google-auth",
        "google-auth-oauthlib",
        "google-api-python-client",
        "fastmcp",
    ],
)