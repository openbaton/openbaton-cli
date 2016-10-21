import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="openbaton-cli",
    version="2.2.1-beta1",
    author="Open Baton",
    author_email="dev@openbaton.org",
    description="The Open Baton CLI",
    license="Apache 2",
    keywords="python vnfm nfvo open baton openbaton sdk cli rest",
    url="http://openbaton.github.io/",
    packages=find_packages(),
    scripts=["openbaton"],
    install_requires=['requests', 'texttable', 'tabulate'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        'Topic :: Software Development :: Build Tools',
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
    ],
    entry_points={
        'console_scripts': [
            'openbaton = org.openbaton.cli.openbaton:start',
        ]
    }
)
