import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), 'r') as fp:
    readme = fp.read()

with open(os.path.join(here, 'requirements.txt'), 'r') as fp:
    install_requires = filter(None, fp.readlines())

with open(os.path.join(here, 'VERSION'), 'r') as fp:
    version = fp.read().strip()

setup(
    name="babblelicious",
    version=version,
    url='http://github.com/smn/babblelicious',
    license='BSD',
    description="#hashtagchat",
    long_description=readme,
    author='Simon de Haan',
    author_email='simon@praekeltfoundation.org',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'Framework :: Twisted',
    ],
)
