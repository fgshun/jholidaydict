from setuptools import setup

py_modules = ['jholidaydict', 'test_jholidaydict']

setup(
        name='jholidaydict',
        version='0.1.0',
        author='fgshun',
        author_email='fgshun@gmail.com',
        url='http://www.lazy-moon.jp/',
        license='MIT',
        py_modules=py_modules,
        setup_requires=['pytest-runner'],
        tests_require=['pytest'])
