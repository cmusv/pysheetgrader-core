
from setuptools import setup, find_packages

setup(
    name='pysheetgrader',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'openpyxl', 'sympy', 'click', 'pyYAML'
    ],
    entry_points='''
        [console_scripts]
        pysheetgrader=pysheetgrader.main:cli
    ''',
    package_dir={'pysheetgrader': 'pysheetgrader'},
    package_data={'pysheetgrader': ['template/*.jinja']}
)
