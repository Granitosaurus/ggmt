from setuptools import setup

setup(
    name='gosuticker',
    version='0.3',
    packages=['gosuticker'],
    url='https://github.com/Granitosaurus/gosuticker',
    license='GPLV3+',
    author='Bernardas Alisauskas',
    author_email='bernardas.alisauskas@gmail.com',
    description='matchticker for gosugamers',
    install_requires=[
        'click',
        'requests',
        'parsel',
        'jinja2'
    ],
    entry_points="""
        [console_scripts]
        gosuticker=gosuticker.cli:cli
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
