from setuptools import setup, find_packages

setup(
    name="karaoke_b3",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'python-mpv>=1.0.0',
        'PyGObject>=3.36.0',
    ],
    entry_points={
        'console_scripts': [
            'karaoke-b3=karaoke_b3.main:main',
        ],
    },
    author="Il Tuo Nome",
    author_email="tua@email.com",
    description="Un'applicazione karaoke con supporto a doppio schermo",
    license="GPL-3.0",
    keywords="karaoke mpv gtk",
    url="https://github.com/tuonome/karaoke-b3",
    python_requires='>=3.6',
)
