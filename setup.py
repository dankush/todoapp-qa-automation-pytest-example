# This setup.py is used to make the test automation framework installable as a package
# It enables importing modules across the project without path manipulation
from setuptools import setup, find_packages

setup(
    name="todoapp-qa-automation",
    version="0.1.0",
    packages=find_packages(),
    description="Playwright automation framework for testing the React Cool Todo App",
    author="QA Team",
    install_requires=[
        "pytest>=7.4.0",
        "pytest-playwright>=0.4.3",
        "playwright>=1.40.0",
        "pytest-xdist>=3.3.1",
        "pytest-html>=4.1.1",
        "ruff>=0.1.6",
        "pytest-dotenv>=0.5.2",
        "allure-pytest>=2.13.2",
    ],
    python_requires=">=3.9",
)
