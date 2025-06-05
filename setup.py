from setuptools import setup

setup(
    name='vip-patroni',
    version='0.1.0',
    py_modules=['vip'],
    install_requires=[
        'arprequest==0.3',
        'docopt==0.6.2',
        'iproute==0.0.1',
        'pyroute2==0.9.2',
        'scapy==2.6.1',
    ],
    entry_points={
        'console_scripts': [
            'vip=vip:main',
        ]
    },
)
