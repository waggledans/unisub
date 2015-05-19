try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
config = {
    'description': 'Allows users to combine several subtitles into one',
    'author': 'Dan Slov',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'dan.slov@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['NAME'],
    'scripts': [],
    'name': 'unisub'
}

setup(**config)