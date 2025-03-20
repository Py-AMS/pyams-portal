#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""
This module contains PyAMS portal package
"""
import os
from setuptools import setup, find_packages


DOCS = os.path.join(os.path.dirname(__file__),
                    'docs')

README = os.path.join(DOCS, 'README.rst')
HISTORY = os.path.join(DOCS, 'HISTORY.rst')

version = '2.6.0'
long_description = open(README).read() + '\n\n' + open(HISTORY).read()

tests_require = [
    'pyams_catalog',
    'pyams_form',
    'pyams_zmi',
    'pyramid_zcml',
    'zope.exceptions'
]

setup(name='pyams_portal',
      version=version,
      description="PyAMS portlets management package",
      long_description=long_description,
      classifiers=[
          "License :: OSI Approved :: Zope Public License",
          "Development Status :: 4 - Beta",
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='Pyramid PyAMS',
      author='Thierry Florac',
      author_email='tflorac@ulthar.net',
      url='https://pyams.readthedocs.io',
      license='ZPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=[],
      include_package_data=True,
      package_data={'': ['*.zcml', '*.txt', '*.pt', '*.pot', '*.po', '*.mo',
                         '*.png', '*.gif', '*.jpeg', '*.jpg', '*.css', '*.js']},
      zip_safe=False,
      # uncomment this to be able to run tests with setup.py
      test_suite="pyams_portal.tests.test_utilsdocs.test_suite",
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'persistent',
          'pyams_file',
          'pyams_i18n',
          'pyams_layer',
          'pyams_pagelet',
          'pyams_security',
          'pyams_sequence',
          'pyams_site',
          'pyams_skin > 2.1.0',
          'pyams_template',
          'pyams_utils >= 2.2.0',
          'pyams_workflow',
          'pyramid >= 2.0.0',
          'venusian',
          'zope.annotation',
          'zope.container',
          'zope.contentprovider',
          'zope.copy',
          'zope.interface',
          'zope.lifecycleevent',
          'zope.location',
          'zope.schema',
          'zope.traversing'
      ],
      entry_points={
          'fanstatic.libraries': [
              'pyams_portal = pyams_portal.zmi:library'
          ]
      })
