import os
import codecs
import setuptools


import myqiwi as lib

here = os.path.abspath(os.path.dirname(__file__))


with open("requirements.txt", encoding="utf-8") as r:
    requires = [i.strip() for i in r] # Зависимости

with open("README.md", "r", "utf-8") as f:
    readme = f.read()


# Получение данных из файла version
about = {}
path = os.path.join(here, "myqiwi", "__version__.py")
with codecs.open(path, "r", "utf-8") as f:
    exec(f.read(), about)

include = ["requirements.txt", "README.md"]

setuptools.setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    packages=setuptools.find_packages(include=include),
    include_package_data=True,
    python_requires=">=3.5",
    install_requires=requires,
    license=about["__license__"],
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: Russian",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    project_urls={"Source": about["__url__"]},
)