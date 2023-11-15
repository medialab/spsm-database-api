from setuptools import find_packages, setup

setup(
    name="spsm-database-api",
    version="0.0.1",
    description="Command-line interface for exporting data relations from SPSM database.",
    author="Kelly Christensen",
    keywords="postgresql",
    license="GPL-3.0",
    python_requires=">=3.11",
    packages=find_packages(exclude=["test"]),
    install_requires=[
        "click==8.1.7",
        "duckdb==0.9.2",
        "markdown-it-py==3.0.0",
        "mdurl==0.1.2",
        "psycopg2==2.9.9",
        "pyaml==23.9.7",
        "Pygments==2.16.1",
        "PyYAML==6.0.1",
        "rich==13.6.0",
    ],
    entry_points={
        "console_scripts": ["spsm=src.main:cli"],
    },
    zip_safe=True,
)
