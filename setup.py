"""Setup for the markdown XBlock."""

import os
from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='markdown-xblock',
    version='0.1',
    description='markdown XBlock',
    packages=[
        'mdown',
    ],
    install_requires=[
        'XBlock',
        'xblock-utils',
        'markdown2>=2.3.0',
        'Pygments>=2.0.2'
    ],
    entry_points={
        'xblock.v1': [
            'mdown = mdown:MarkdownXBlock',
        ]
    },
    package_data=package_data("mdown", ["static", "public"]),
)
