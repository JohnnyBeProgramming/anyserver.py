import subprocess
from distutils.core import setup

name = 'anyserver'
version = '0.1'

print(f'SETUP {name} [{version}]')
setup(
    name=name,
    packages=[
        name,
        f'{name}.encoders',
        f'{name}.servers',
    ],
    version=version,
    license='MIT',
    description='Simple and generic python web server and utils',
    author='Club404',
    author_email='info@club404.io',
    url='https://github.com/JohnnyBeProgramming/anyserver.py',
    download_url='https://github.com/JohnnyBeProgramming/anyserver.py/archive/refs/tags/%s.tar.gz' % version,
    keywords=['simple', 'http', 'server'],
    install_requires=[],
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
