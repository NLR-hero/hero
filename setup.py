from setuptools import setup


setup(name='gantry',
      version='0.0.1',
      packages=['gantry'],
      entry_points={
          'console_scripts': ['gantry=gantry.command_line:main'],
      },
      install_requires=['requests'],  # list dependencies
      )
