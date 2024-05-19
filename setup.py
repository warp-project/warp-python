from setuptools import setup, find_packages
import os

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()
    
VERSION = '1.2.16'

setup(
    name='warp-python',
    version=VERSION,
    author='warp-project, Ryan_shamu',
    author_email='simon.c.gilde@gmail.com, ryanshamu418@gmail.com',
    description='A python module for WARP',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/warp-project/warp-python',
    packages=find_packages(exclude=[]),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords=['warp'],
    install_requires=[
        'requests',
        'Flask',
    ],
    python_requires='>=3.8',
)
