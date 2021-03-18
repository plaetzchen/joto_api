from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='joto_api',
      version='0.1.1',
      description='A package to interact with api.joto.io',
      long_description=readme(),
      long_description_content_type="text/markdown",
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
      ],
      keywords='joto api',
      url='http://github.com/plaetzchen/joto_api',
      author='Philip Brechler',
      author_email='pbrechler@mac.com',
      license='MIT',
      packages=['joto_api'],
      install_requires=[
          'requests',
      ],
      zip_safe=False)
