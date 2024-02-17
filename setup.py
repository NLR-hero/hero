from setuptools import setup

__version__ = "0.0.1"
requires = [
    "boto3>=1.28.3",
    "psycopg2-binary>=2.9.6",
    "requests>=2.28.2",
    "pyyaml>=6.0",
    "pytest>=7.4.0",
    "numpy",
]


setup(
    name="hero",
    version=__version__,
    packages=["hero", "hero.api", "hero.aws", "hero.auth", "hero.config"],
    install_requires=requires,
    setup_requires=requires,
    entry_points={
        "console_scripts": [
            "hero_clear_queue=hero.bin.hero_clear_queue:main",
        ]
    },
)
