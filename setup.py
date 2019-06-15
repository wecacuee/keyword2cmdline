from setuptools import setup, find_packages

setup(name='keyword2cmdline',
      description='Keyword arguments of a function as command-line arguments',
      author='Vikas Dhiman',
      url='https://github.com/wecacuee/keyword2cmdline',
      author_email='dhiman@umich.edu',
      version='1.3.0',
      license='MIT',
      classifiers=(
          'Development Status :: 3 - Alpha',
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ),
      python_requires='>=3.5',
      py_modules=['keyword2cmdline', 'functoolsplus'],
      install_requires=['kwplus'],
      setup_requires=["pytest-runner"],
      tests_require=["pytest"],
      extras_require={
          'argcomplete': ['argcomplete']
      })
