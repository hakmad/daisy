import setuptools


setuptools.setup(
    name="daisy",
    py_modules=["daisy"],
    install_requires=[
        "Jinja2",
        "Markdown",
    ],
    entry_points={
        "console_scripts": [
            "daisy = daisy:main",
        ],
    },
)
