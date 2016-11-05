from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from codecs import open
from os import path
import sys

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


class PyTest(TestCommand):
    def run_tests(self):
        self.pytest_args = ['-vvv', '-l']
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(name='fdns',
      version='0.1.0',
      description='Forwarding DNS',
      long_description=long_description,
      packages=find_packages(),
      author='Shengjing Zhu',
      author_email='zsj950618@gmail.com',
      url='https://github.com/zhsj/fdns',
      license='MIT',
      install_requires=['aiohttp', 'dnslib'],
      tests_require=['pytest'],
      cmdclass={'test': PyTest},
      entry_points={
          'console_scripts': [
              'fdns=fdns.app:main',

          ]
      }
      )
