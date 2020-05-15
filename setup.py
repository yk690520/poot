from setuptools import find_packages,setup
setup(
    name = 'poot',     #pypi中的名称，pip或者easy_install安装时使用的名称
    version = '2.7',
    author ='Junx',
    author_email='yk690520@outlook.com',
    packages = find_packages(),

    #需要安装的依赖
    install_requires=[
        'airtest>=1.0.27'
    ],

    # 此项需要，否则卸载时报windows error
    zip_safe=False

)