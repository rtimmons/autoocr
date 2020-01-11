from setuptools import setup

version = "0.0.0"

f = open("README.md")
try:
    try:
        readme_content = f.read()
    except:
        readme_content = ""
finally:
    f.close()

setup(
    name="autoocr",
    version=version,
    description="Automatically Run PDFSandwich",
    long_description=readme_content,
    author="Ryan Timmons",
    author_email="ryan <at> rytim.com",
    maintainer="Ryan Timmons",
    maintainer_email="ryan <at> rytim.com",
    url="http://github.com/rtimmons",
    keywords=[],
    install_requires=[
        "filelock==3.0.12",
    ],
    license="Apache License, Version 2.0",
    python_requires=">=3.5",
    classifiers=[],
    packages=['autoocr'],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'autoocr = autoocr.cli:main'
        ]
    }
)
