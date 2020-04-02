import re

from poot.core.api import Poot

poot=Poot('5LM7N16812002521')

print(poot(resource_id="com.minxing.client:id/btn_login").get_text())