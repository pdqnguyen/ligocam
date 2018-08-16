#!/usr/bin/env python
#
# Project Librarian: Dipongkar Talukder
#                    Postdoctoral Scholar
#                    University of Oregon / LIGO Scientific Collaboration
#                    <dipongkar.talukder@ligo.org>
#
# Copyright (C) 2013 Dipongkar Talukder
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
import os

data_files = []
for root, dirnames, filenames in os.walk('etc'):
    for filename in filenames:
        path = os.path.join(root, filename)
        data_files.append((root, path))
setup(
    name='ligocam',
    version='0.0',
    url='http://pem.ligo.org',
    author='Dipongkar Talukder',
    author_email='dipongkar.talukder@ligo.org',
    description='LIGO Channel Activity Monitor',
    license='GNU General Public License Version 3',
    packages=find_packages(),
    include_package_data=True,
    scripts=[
        'bin/ligocam',
        'bin/ligocam-batch',
        'bin/ligocam-post',
        'bin/ligocam-setup'
    ],
    data_files=data_files
)
