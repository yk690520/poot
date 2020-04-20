import re

from poot.core.api import Poot

poot=Poot('5LM7N16812002521')
t=poot(text='搜索').get_bounds()
print(t)