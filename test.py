import re

from poot.core.api import Poot

poot=Poot('5LM7N16812002521')
print(poot.adb.exe_cmd('push','C:\\Users\\yk690520\\PycharmProjects\\TFAnYi\\static\\.A1','/mnt/sdcard'))