from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='pubmed_timeline',
      version='0.1',
      description='Create timelines of important terms in biomedical literature.',
      long_description=readme(),
      url='https://github.com/rgarcia-herrera/pubmed_timeline',
      author='Rodrigo Garcia',
      author_email='rgarcia@riseup.net',
      license='GPL3',
      packages=['pubmed_timeline'],
      install_requires=['pattern',
                        'networkx',
                        'biopython',],
      include_package_data=True,
      scripts=['bin/pubmed_timeline_top_degree'],
      zip_safe=False
      #TODO: include tests in setup with pytest
      )
