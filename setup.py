from setuptools import setup, find_packages

setup(
    name='fonts-compare',
    version='1.2.7',
    description='A tool to compare fonts',
    author='Sudip Shil',
    author_email='sudipshil9862@gmail.com',
    packages=find_packages(),
    install_requires=[
        'PyGObject',
        'langdetect',
        'langtable',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
