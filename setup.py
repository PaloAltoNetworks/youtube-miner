from setuptools import Extension, setup, find_packages

import sys
import os.path
sys.path.insert(0, os.path.abspath('.'))

from youtubeminer import __version__

with open('requirements.txt') as f:
    _requirements = f.read().splitlines()

setup(
    name='youtube-miner',
    version=__version__,
    author='Palo Alto Networks',
    author_email='techbizdev@paloaltonetworks.com',
    description='Sample MineMeld node extension for mining Youtube API',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Security',
        'Topic :: Internet'
    ],
    packages=find_packages(),
    provides=find_packages(),
    install_requires=_requirements,
    package_data = {
        '': ['prototypes/*.yml']
    },
    entry_points={
        'minemeld_nodes': [
            'youtubeminer.Miner = youtubeminer.node:Miner'
        ],
        'minemeld_prototypes': [
            'youtubeminer.prototypes = youtubeminer:prototypes'
        ]
    }
)
