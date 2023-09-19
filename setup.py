from setuptools import setup


setup(
    name='hero',
    version='0.0.1',
    packages=['hero', 'hero.api', 'hero.aws', 'hero.auth', 'hero.config'],
    install_requires=[
        'boto3>=1.28.3',
        'psycopg2-binary>=2.9.6',
        'requests>=2.28.2'
    ]
)