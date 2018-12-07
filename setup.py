from setuptools import setup, find_packages

setup(name='keyword2cmdline',
      description='Keyword arguments of a function as command-line arguments',
      author='Vikas Dhiman',
      url='https://github.com/wecacuee/keyword2cmdline',
      author_email='dhiman@umich.edu',
      version='0.1.1',
      license='MIT',
      classifiers=(
          'Development Status :: 3 - Alpha',
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ),
      python_requires='>=3.5',
      packages=find_packages(),
      setup_requires=["pytest-runner"],
      tests_require=["pytest"])
