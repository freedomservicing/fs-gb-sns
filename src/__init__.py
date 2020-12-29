from setuptools import setup, find_packages

setup(
    name = 'fs-gb-sns',
    version = '0.0.1',
    description = 'Freedom Servicing GB Listener',
    url = 'https://github.com/freedomservicing/gb_sns',
    author = 'Freedom Servicing, LLC',
    author_email = 'dev@freedomgateway.llc',
    license = 'MIT',
    install_requires = ["argparse", "json", "time", "threading", "firebase_admin", "mysql.connector", "os"],
    packages = find_packages(),
    entry_points = dict(
        console_scripts = ['rq=src.sns:main']
    )
)
