from setuptools import find_packages, setup

import export_csv

try:
    readme = open('README.rst').read()
except IOError:
    readme = ''

setup(
    name='django-csv-export',
    version='.'.join(str(i) for i in export_csv.VERSION),
    description='django-export-csv is a reusable Django application which '
                'provides generic View class for creating and rendering CSV.',
    long_description=readme,
    packages=find_packages(exclude=('tests', 'docs', 'example', )),
    author='Narendra Choudhary',
    author_email='narendralegha.mail@gmail.com',
    url='https://github.com/narenchoudhary/django-export-csv/tree/master',
    install_requires=['Django>=1.7'],
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='django library development',
    zip_safe=False,
)
