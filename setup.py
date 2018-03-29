from setuptools import setup

setup(
    name='ggmt',
    version='0.9.3',
    packages=['ggmt'],
    url='https://github.com/Granitosaurus/ggmt',
    license='GPLV3+',
    author='Bernardas Ališauskas',
    author_email='bernardas.alisauskas@gmail.com',
    description='Good Game Match Ticker - command line application for tracking matches of various e-sport games',
    install_requires=[
        'click',
        'requests',
        'parsel',
        'jinja2',
        'colorama'
    ],
    entry_points="""
        [console_scripts]
        ggmt=ggmt.cli:cli
    """,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ]
)
