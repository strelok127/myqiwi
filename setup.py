import os
import codecs 
import setuptools

# Получение текущей директории
here = os.path.abspath(os.path.dirname(__file__)) 

# Название плагина
packages = ["myqiwi"]

#Зависимости
requires = [] # Список зависимостей
path_2_requirements = os.path.join(here, "requirements.txt")
with codecs.open(path_2_requirements, "r", "utf-8") as f:
    for requir in f.readlines():
        requires.append(requir[:-2])


# Получение данных из файла version
about = {}
path = os.path.join(here, "myqiwi", "__version__.py")
with codecs.open(path, "r", "utf-8") as f:
    exec(f.read(), about)


# Получение readme
with codecs.open("README.md", "r", "utf-8") as f:
    readme = f.read()


# Получение истории обновлений
with codecs.open("HISTORY.md", "r", "utf-8") as f:
    history = f.read()


setuptools.setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    packages=packages,
    include_package_data=True,
    python_requires=">=3.5",
    install_requires=requires,
    zip_safe=False,

    package_dir={"myqiwi": "myqiwi"},
    project_urls={"Source": about["__url__"]}
    )

