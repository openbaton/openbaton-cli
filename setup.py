import os

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="openbaton-cli",
    version="6.0.0",
    author="Open Baton",
    author_email="dev@openbaton.org",
    description="The Open Baton CLI",
    license="Apache 2",
    keywords="python vnfm nfvo open baton openbaton sdk cli rest",
    url="http://openbaton.github.io/",
    packages=find_packages(),
    scripts=["openbaton", "openbaton-v2"],
    install_requires=[
        'requests',
        'tabulate',
        'argcomplete',
        'configparser',
        'asyncio',
        'cliff',
    ],
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
        ],
        'openbaton.cmd': [
            'nsd = org.openbaton.v2.nsd:Nsd',
            'nsr = org.openbaton.v2.nsr:Nsr',
            'project = org.openbaton.v2.projects:Projects',
            'vim = org.openbaton.v2.vims:Vims',
            'event = org.openbaton.v2.events:Events',
            'package = org.openbaton.v2.packages:VnfPackages',
            'user = org.openbaton.v2.users:Users',
            'service = org.openbaton.v2.services:Services',
            'market = org.openbaton.v2.market:Market',
            'script = org.openbaton.v2.scripts:Scripts',
            'key = org.openbaton.v2.keys:Keys',
        ]
    }
)
