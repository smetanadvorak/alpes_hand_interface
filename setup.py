from setuptools import setup, find_packages

setup(
    name='Alpes',
    version = '1.0',
    packages = find_packages(),
    install_requires = ['pyserial>=3.4', 'numpy>=1.18.1'],
    author = 'Konstantin Akhmadeev',
    author_email = 'kakhmadeev@gmail.com',
    description = 'This package provides tools for working with a specific model of robotic hands available in LS2N laboratory.',
    url = 'https://github.com/smetanadvorak/alpes_hand_interface'
)