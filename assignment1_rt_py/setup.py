from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'assignment1_rt_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='stefania.germena3@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'distance = assignment1_rt_py.distance_calc:main',
            'turtles = assignment1_rt_py.two_turtles:main',
            'turtle2 = assignment1_rt_py.turtle_spawn:main',
        ],
    },
)
