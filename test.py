import re

from poot.core.api import Poot

poot=Poot('5LM7N16812002521')


uis=poot(text="大额审批").sibling()

for ui in uis:
    print(ui.get)