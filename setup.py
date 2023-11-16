from setuptools import setup
from hero import __version__

setup(
    name='hero',
    version=__version__,
    packages=['hero', 'hero.api', 'hero.aws', 'hero.auth', 'hero.config'],
    entry_points={ "console_scripts": [
                        "hero_clear_queue=hero.bin.hero_clear_queue:main",
            ]},
)