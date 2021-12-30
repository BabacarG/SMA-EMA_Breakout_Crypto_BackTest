from CryptoBackTest import *

api_key = 'WDpBVEVMc3wjLCAYQ4opBgpHNhDlT0ClZH25OZml4C0ocygkDR30JggMOr5kKYrK'
api_secret = '51iVBjoSMhu4NkU85d7SiVrGpMwOB2eyPTHbvKe1zW1iHWquhXqg3rIwcu29anKK'
asset = "BTCUSDT"
timeFrame = "4hours"
startDate = "1 Sep, 2019"
test1 = CryptoBackTest(api_key, api_secret, asset, timeFrame, startDate)
# test1.buysell1ema()
# test1.buy1ema()
# test1.buy2ema()
test1.buy3ema()
