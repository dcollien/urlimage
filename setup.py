import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="urlimage-dcollien",
    version="0.0.1",
    author="David Collien",
    author_email="me@dcollien.com",
    description="Infers an image to use for a given URL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dcollien/urlimage",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
