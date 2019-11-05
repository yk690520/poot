import poot
from poot.poot.poot import Poot


@poot.poot_thread
def test(deviceId):

    pooter=Poot(deviceId)
    with pooter.freeze() as poote:
        poote("微信").tap()
        poote("蒂凡尼小家").tap()

if __name__=="__main__":
    poot.run()