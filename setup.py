from setuptools import setup

setup(
    name='sfmtwitterharvester',
    version='1.0.0',
    url='https://github.com/gwu-libraries/sfm-twitter-harvester',
    author='Justin Littman',
    author_email='justinlittman@gmail.com',
    description="Social Feed Manager Twitter Harvester",
    platforms=['POSIX'],
    test_suite='tests',
    scripts=['twitter_harvester.py',
             'twitter_rest_warc_iter.py',
             'twitter_stream_warc_iter.py'],
    install_requires=['sfmutils',
                      'python-dateutil>=2.4.2'],
    tests_require=['mock>=1.3.0'],
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.7',
        'Development Status :: 4 - Beta',
    ],
)