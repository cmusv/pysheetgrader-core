from setuptools import setup, find_packages

setup(
    name='pysheetgrader',
    version='0.3',
    packages=find_packages(),
    install_requires=[
        'openpyxl', 'sympy', 'click', 'pyYAML'
    ],
    entry_points='''
        [console_scripts]
        pysheetgrader=pysheetgrader.main:cli
    '''
)
