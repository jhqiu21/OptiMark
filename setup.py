from setuptools import setup, find_packages

setup(
  name="optimark",
  version="0.1.0",
  packages=find_packages(),
  install_requires=[
    "pymysql", "python-dotenv", "click"
  ],
  entry_points={
    "console_scripts": [
      "optimark=optimark.cli.db_cli:cli"
    ]
  }
)