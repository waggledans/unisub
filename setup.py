# encoding: utf-8
import setuptools

version = "1.0.0"


# Generate Requirements
requirements = list()
with open("requirements.txt", 'r') as f:
    for line in (l.strip() for l in f.readlines()):
        if not line or line.startswith(('#', 'setuptools', 'pip')):
            continue
        requirements.append(line)

setuptools.setup(
    name="unisub",
    version=version,
    description='Manipulating mandarin subtitles (.srt) file',
    long_description='''
        Unisub allows merge 2 different subtitles files together, as well
        as converting mandarin characters (hanzi) into pinyin
        ''',
    url="https://github.com/waggledans/unisub",
    author="Dan Slov",
    author_email="dan.slov@gmail.com",
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Topic :: Movies',
        'Topic :: Movies :: Subtitles',
        'Topic :: Chinese :: pinyin'
    ],
    test_suite='tests',
    packages = [
        'unisub'
        ],
    entry_points={
        'bin': [
            'merge = merge:main',
        ],
    },
    package_data={
        "unisub": [
            'LICENSE',
        ],
    },
    install_requires=requirements
)
