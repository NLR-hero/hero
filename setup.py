from setuptools import setup

# from hero import __version__

setup(
    name="hero",
    version="0.1.5",
    packages=["hero", "hero.auth"],
    entry_points={
        "console_scripts": [
            "hero_clear_queue=hero.bin.hero_clear_queue:main",
        ]
    },
)
