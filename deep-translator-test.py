# Only GoogleTranslator worked without error

from deep_translator import GoogleTranslator
from deep_translator import PonsTranslator
from deep_translator import LingueeTranslator

# Google
word_list = ['妹', '駅', '侍', 'お土産', '魚', '白血球', '糖尿病', '恥', '失速する']
wordlist_translated_by_google = []
for i in range(len(word_list)):
    translated = GoogleTranslator(source='ja', target='fr').translate(word_list[i])
    wordlist_translated_by_google.append(translated)
print(wordlist_translated_by_google)


# Pon
# wordlist_translated_by_pon = []
# for i in range(len(word_list)):
#     translated = PonsTranslator(source='ja', target='fr').translate(word_list[i], return_all=False)
#     wordlist_translated_by_pon.append(translated)
# print(wordlist_translated_by_pon)


# Linguee
wordlist_translated_by_linguee = []
print(word_list)
for i in range(len(word_list)):
    translated = LingueeTranslator(source='japanese', target='french').translate(word_list[i])
    wordlist_translated_by_linguee.append(translated)
print(wordlist_translated_by_linguee)