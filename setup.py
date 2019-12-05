from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='exp_management',
    version='0.0.1',
    description='A library designed to help run numerical experiments.',
    long_description=readme,
    author='Geoffrey Bradway',
    author_email='geoff.bradway@gmail.com',
    url='https://github.com/zoso95/exp_management',
    license=license,
    packages=find_packages(exclude=('tests', 'examples')),
    install_requires=requirements,
)
