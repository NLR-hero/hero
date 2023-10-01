from setuptools import setup
from hero import __version__

setup(
    name='hero',
    version=__version__,
    packages=['hero', 'hero.api', 'hero.aws', 'hero.auth', 'hero.config'],
    install_requires=[
        'boto3>=1.28.3',
        'psycopg2-binary>=2.9.6',
        'requests>=2.28.2'
    ],
    entry_points={ "console_scripts": [
                        "hero_clear_queue=hero.hero_clear_queue:main",
            ]},
)