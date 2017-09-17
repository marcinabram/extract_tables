"""Setup file that allow to install the module using pip."""
import setuptools


setuptools.setup(
    name='extract_tables',
    version='1.0',
    description='Project for extracting tables from pdfs.',
    author='Marcin Abram',
    author_email='abram.mj@gmail.com',
    packages=setuptools.find_packages(),
    install_requires=[
        'wheel>=0.29.0,<1.0.0',
        'coverage>=4.4.1,<5.0.0',
        'tabula-py>=1.0.0,<1.1.0',
        'PyPDF2>=1.26,<2.0',
        'pdfminer.six==20170720',
    ],
    dependency_links=[],
    test_suite='extract_tables.tests',
)
