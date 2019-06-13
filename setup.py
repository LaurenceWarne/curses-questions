from setuptools import setup, find_packages


setup(
    name="curses questions",
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3',
    url="https://github.com/LaurenceWarne/curses-questions",
    version="1.1",
    author="Laurence Warne",
    license="MIT",
    entry_points={
        'console_scripts':
        ['curses-questions=curses_questions.scripts.ask_questions:main'],
    },
    install_requires=[],
    zip_safe=False
)
