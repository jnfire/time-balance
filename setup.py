from setuptools import setup, find_packages

import os

def get_version():
    version_path = os.path.join(os.path.dirname(__file__), 'time_balance', 'VERSION')
    with open(version_path, 'r') as f:
        return f.read().strip()

setup(
    name='time-balance',
    version=get_version(),
    description='Professional tool to manage projects and track workday balances.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    package_data={
        'time_balance': ['VERSION', 'i18n/locales/*.json'],
    },
    install_requires=[
        'rich>=10.0.0',
    ],
    entry_points={
        'console_scripts': [
            'time-balance=time_balance.cli.main:main',
        ],
    },
    author='Javier',
    license='GPL-3.0-only',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
)
