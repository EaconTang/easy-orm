from setuptools import setup

VERSION = '0.0.1'
DESCRIPTION = "EasyORM: A simple orm implementation"
LONG_DESCRIPTION = open('README.md').read()

CLASSIFIERS = filter(None, map(str.strip,
"""
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Programming Language :: Python :: 3",
Operating System :: OS Independent
Topic :: Utilities
Topic :: Database :: Database Engines/Servers
Topic :: Software Development :: Libraries :: Python Modules
""".splitlines()))

setup(
    name="easyorm",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    keywords=('mysql', 'orm', 'databse'),
    author="Eacon Tang",
    author_email="tyingk@163.com",
    url="https://github.com/EaconTang/easy-orm",
    license="MIT License",
    platforms=['any'],
    test_suite="",
    zip_safe=True,
    install_requires=['PyMySQL==0.7.9'],
    packages=['easyorm']
)