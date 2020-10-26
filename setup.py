from setuptools import setup

setup(
    name='pysheetgrader',
    version='0.1',
    py_modules=['pysheetgrader'],
    install_requires=[
        'openpyxl', 'sympy', 'click'
    ],
    entry_points='''
        [console_scripts]
        pysheetgrader=main:cli
    '''
)
