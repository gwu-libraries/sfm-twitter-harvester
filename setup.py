from setuptools import setup

setup(
    name='sfmtwitterharvester',
    version='2.0.2',
    url='https://github.com/gwu-libraries/sfm-twitter-harvester',
    author='Social Feed Manager',
    author_email='sfm@gwu.edu',
    description="Social Feed Manager Twitter Harvester",
    platforms=['POSIX'],
    test_suite='tests',
    scripts=['twitter_harvester.py',
             'twitter_rest_warc_iter.py',
             'twitter_stream_warc_iter.py'],
    install_requires=['sfmutils',
                      'python-dateutil>=2.7.5'],
    tests_require=['mock==2.0.0'],
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
    ],
)
