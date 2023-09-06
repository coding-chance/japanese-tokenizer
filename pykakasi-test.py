import pykakasi
kks = pykakasi.kakasi()
text = "明後日"
result = kks.convert(text)
print(result)
# for item in result:
#     print("{}: kana '{}', hiragana '{}', romaji: '{}'".format(item['orig'], item['kana'], item['hira'], item['hepburn']))