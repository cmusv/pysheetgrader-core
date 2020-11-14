from setuptools import setup

setup(
    name='pysheetgrader',
    version='0.2',
    py_modules=['pysheetgrader'],
    install_requires=[
        'openpyxl', 'sympy', 'click', 'pyYAML'
    ],
    entry_points='''
        [console_scripts]
        pysheetgrader=main:cli
    '''
)
