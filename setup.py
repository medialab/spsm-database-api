from setuptools import find_packages, setup

setup(
    name="spsm-database-api",
    version="0.0.1",
    description="Command-line interface for exporting data from SPSM database.",
    author="Kelly Christensen",
    keywords="postgresql",
    license="GPL-3.0",
    python_requires=">=3.11",
    packages=find_packages(exclude=["test"]),
    install_requires=[
        "click==8.1.7",
        "markdown-it-py==3.0.0",
        "mdurl==0.1.2",
        "pip==24.0",
        "Pygments==2.17.2",
        "psycopg2==2.9.9",
        "PyYAML==6.0.1",
        "pyaml==23.12.0",
        "rich==13.7.0",
        "setuptools==65.5.0",
        "SQLAlchemy==2.0.27",
        "typing_extensions==4.9.0",
        "casanova==2.0.2",
        "ebbe==1.13.2",
    ],
    entry_points={
        "console_scripts": ["spsm=src.main:cli"],
    },
    zip_safe=True,
)
