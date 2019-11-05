from setuptools import find_packages,setup
setup(
    name = 'poot',     #pypi中的名称，pip或者easy_install安装时使用的名称

    version = '0.1',
    author ='anll',
    author_email='yk690520@outlook.com',
    description='This is a plugins for uediter',
    keywords='android',
    url='https://github.com/yk690520/origin/tree/master/python/ueflask',
    packages = find_packages(),

    #需要安装的依赖
    install_requires=[
        'flask>=1.0.2',
        'qiniu>=7.2.2'
    ],

    # 此项需要，否则卸载时报windows error
    zip_safe=False

)