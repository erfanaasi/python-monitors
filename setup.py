import setuptools

from distutils.core import setup
from distutils import util

if __name__ == "__main__":

    setup ( name = 'python-monitors',
            version='0.1.1',
            author='Dogan Ulus',
            author_email='doganulus@gmail.com',
            url='http://github.com/doganulus/python-monitors/',
            packages=setuptools.find_packages(),
            license='GPLv3+',
            classifiers=[
                'Development Status :: 3 - Alpha',
                'Intended Audience :: Developers',
                'Intended Audience :: Science/Research',
                'Topic :: Scientific/Engineering',
                'Topic :: Scientific/Engineering :: Mathematics',
                'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                'Programming Language :: Python :: 2',
            ],
            description = 'A pure Python package to monitor formal specifications over temporal sequences',
            python_requires='>=2',
            install_requires=[
                'python-intervals',
                'antlr4-python2-runtime'
            ],
            include_package_data=True,
    )

