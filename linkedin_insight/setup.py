from setuptools import setup, find_packages

setup(
    name="linkedin_insight",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "selenium",
        "beautifulsoup4",
        "requests",
        "python-dotenv",
        "graphviz",
        "jinja2",
        "webdriver_manager",
    ],
    entry_points={
        "console_scripts": [
            "linkedin_insight=src.main:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A LinkedIn company insights scraper",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/linkedin_insight",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)