from setuptools import setup
import versioneer

requirements = [
    "medcoupling",
]

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='medpro',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Medcoupling based post processing tools",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="MIT",
    author="Luca Dall Olio",
    author_email='luca.dallolio@gmail.com',
    url='https://github.com/ldallolio/medpro',
    packages=['medpro'],
    
    install_requires=requirements,
    keywords=['medpro', 'medcoupling'],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
