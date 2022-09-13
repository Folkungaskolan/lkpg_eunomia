from setuptools import setup

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()
    fh.close()

setup(
    name="helloworld",
    url="https://github.com/Folkungaskolan/lkpg_eunomia",
    author='Lyam Dolk',
    author_email='LyamDolk@gmail.com',
    version="0.0.1",
    description="codebase for manageing Linköping municipality student records as demo for programming class",
    long_description=long_description,  # Pull Md from file above
    long_description_content_type="text/markdown",  # specify above docs format
    py_modules=["helloworld"],  # packages i am publishing
    package_dir={"": "src"},  # folder code is in
    # classifiers for finding code i PyPI
    classifiers=["Development Status :: 3 - Alpha",
                 "Programming Language :: Python :: 3.10",
                 "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                 "Operating System :: Microsoft :: Windows :: Windows 10"],
    install_requires=["pandas, selenium, time"],  # production run need thees packages
    extras_require={
        "dev": ["pytest>=3.7", "check-manifest>=4.8", "twine>=4.0.1"]
    }  # for dev you also need thees packages
)
