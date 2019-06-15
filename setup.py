from setuptools import setup, find_packages

setup(name='keyword2cmdline',
      description='Keyword arguments of a function as command-line arguments',
      author='Vikas Dhiman',
      url='https://github.com/wecacuee/keyword2cmdline',
      author_email='wecacuee@github.com',
      long_description=open('README.md', encoding='utf-8').read(),
      long_description_content_type="text/markdown",
      version='2.0.1',
      license='MIT',
      classifiers=(
          'Development Status :: 3 - Alpha',
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ),
      python_requires='>=3.5',
      py_modules=['keyword2cmdline'],
      setup_requires=["pytest-runner"],
      install_requires=["kwplus"],
      tests_require=["pytest"],
      extras_require={
          'argcomplete': ['argcomplete']
      })
