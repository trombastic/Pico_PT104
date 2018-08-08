# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
import PT104


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Operating System :: POSIX',
    'Operating System :: MacOS :: MacOS X',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
]
setup(
    author=PT104.__author__,
    author_email="m.schroeder@tu-berlin.de",
    name='Pico_PT104',
    version=PT104.__version__,
    description='A Python Wrapper for the usbpt104 library from Pico',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url='http://www.github.com/trombastic/Pico_PT104',
    license='GPL version 3',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[],
    packages=find_packages(exclude=["project", "project.*"]),
    include_package_data=True,
    test_suite='runtests.main',
)
