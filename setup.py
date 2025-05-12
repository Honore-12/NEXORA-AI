from setuptools import setup, find_packages

setup(
    name='nexora-agent',
    version='1.0.0',
    author='Vishnu',
    author_email='vishnu.tppr@gmail.com',
    description='Nexora AI– A smart Python voice agent with reminders, WhatsApp, screenshots, and more!',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Vishnu-tppr',
    packages=find_packages(),
    py_modules=["NEXORA AI"],
    install_requires=[
        'pyttsx3',
        'pyautogui',
        'wikipedia',
        'pyjokes',
        'pywhatkit',
        'Pillow',
        'SpeechRecognition',
        'comtypes',
        'pycaw',
        'customtkinter',
        'playsound',
        'word2number',
        'schedule',
        'plyer'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.8',
    include_package_data=True,
)
