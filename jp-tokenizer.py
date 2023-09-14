import pyperclip
import csv
import datetime
import MeCab
import re
from dotenv import load_dotenv
import os
import sys
import pykakasi
from deep_translator import GoogleTranslator
import jaconv

# load environment variable set in .env
load_dotenv()
# Load directory path to the project directory from .env file
TOKENIZER_PROJECT_DIRECTORY = os.environ['TOKENIZER_PROJECT_DIR']




# Combine duplicate words into one.
def exclude_duplicate_word(wordlist):
    no_duplicate_wordlist = []
    for num in wordlist:
        if num not in no_duplicate_wordlist:
            no_duplicate_wordlist.append(num)
    # ↓ Rewrite the code above using list comprehensions (内包表記)
    # [ no_duplicate_wordlist.append(num) for num in extracted_wordlist if not num in no_duplicate_wordlist ] 
    return no_duplicate_wordlist

# Exclude alphabetical words
def exclude_alphabet(wordlist):
    re_japanese = re.compile('[ぁ-んァ-ン一-龥]+')
    re_alphabet = re.compile(r'.*[a-zA-Z\s\.\,]+') # アルファベット判定用正規表現
    no_alphabet_wordlist = []
    for word in wordlist:
        # contain_alphabet = re.match(re_alphabet, word) # アルファベット判定
        contain_alphabet = re.search(r'[a-zA-Z0-9]', word)
        # print(f"contain_alphabet({word}): {contain_alphabet}")
        if word.isascii():
            print(f"{word}はアルファベットを含みます。")      
            word = word.split('-')[0]
            no_alphabet_wordlist.append(word)
        elif re_japanese.findall(word):
            print(f"{word}は日本語を含みます。")      
            no_alphabet_wordlist.append(word)
        

    return no_alphabet_wordlist

# Exclude single-character katakana and hiragana (Stopped using this because it excluded single character kanji)
def exclude_single_char_word(wordlist):
    wordlist_without_single_char = []
    reg_hiragana = re.compile(r'^[あ-ん]+$')
    reg_katakana = re.compile(r'[\u30A1-\u30F4]+')
    for word in wordlist:
        print(f"word({word})")
        if reg_hiragana.fullmatch(word) != True and reg_katakana.fullmatch(word) != True and len(word) != 1:
            wordlist_without_single_char.append(word)
        # print(f'{word} is hiragana?: {reg_hiragana.fullmatch(word)}')
        # print(f'{word} is katakana?: {reg_katakana.fullmatch(word)}')
        # print(f'length of {word}: {len(word)}')
    return wordlist_without_single_char

# Convert phonetics(romaji) for french
def convert_romaji_to_french_phonetic(input_word_list):
    replaced_word_list = []
    convert_necessity_flag = False
    for phonetic in input_word_list:
        replaced_phonetic = phonetic
        # Check if phonetic needs to be converted and convert phonetics
        if phonetic.find('i') != -1 or phonetic.find('e') != -1 or phonetic.find('ch') != -1 or phonetic.find('r') != -1:
            replaced_phonetic = phonetic.replace("i", "ï").replace("e", "é").replace("ch", "tch").replace("r", "l")
            # print(f"Phonetic replaced: {phonetic} -> {replaced_phonetic}")
        replaced_word_list.append(replaced_phonetic)
    return replaced_word_list

def convert_kanji_to_hiragana(kanji_list):
    hiragana_list = []
    kakasi = pykakasi.kakasi()
    re_katakana = re.compile(r'[\u30A1-\u30F4]+')  # カタカナ判定用正規表現
    re_hiragana = re.compile(r'^[あ-ん]+$')  # ひらがな判定用正規表現
    re_kanji = re.compile(r'^[\u4E00-\u9FD0]+$')  # 漢字判定用正規表現
    for word in kanji_list:
        print(word)
        status_katakana = re_katakana.fullmatch(word)  # 単語がカタカナかどうか判定する
        status_hiragana = re_hiragana.fullmatch(word)  # 単語がひらがなかどうか判定する
        status_kanji = re_kanji.fullmatch(word)
        # print(f"status_katakana({word}): {status_katakana}")
        # print(f"status_hiragana({word}): {status_hiragana}")
        # print(f"status_kanji({word}): {status_kanji}")
        hiragana = ""

        if status_kanji:
            hiragana = kakasi.convert(word)[0]['hira']
            print(f"{word} is kanji, converted to {hiragana}")
        elif status_katakana:
            hiragana = jaconv.kata2hira(word)  # katakana -> hiragana
            print(f"{word} is katakana, converted to {hiragana}")
        elif status_hiragana:
            print(f"{word} is already hiragana, no need to convert.")
        else:
            print(f"{word} is mix with kanji and hiragana, converted to {hiragana}.")
            hiragana = kakasi.convert(word)[0]['hira']

        hiragana_list.append(hiragana)
    return hiragana_list

def exclude_stop_words(wordlist):
    stop_words = ["為", "為る", "為す", "呉れる", "有る", "成る", "これ", "あれ", "居る", "私"]
    filtered_words = []
    for word in wordlist:
        # Check if the word is not in the stop_words list
        if word not in stop_words:
            # If the word is not in stop_words, add it to the filtered_words list
            filtered_words.append(word)
    return filtered_words



# Get current time info
dt_now = datetime.datetime.now()
formatted_dt_now = dt_now.strftime('%Y-%m-%d_%H.%M.%S')

# Get data stored in clipboard
copiedText = pyperclip.paste()

# Extract words from text in clipboard
tagger = MeCab.Tagger()
tagger.parse("") # To avoid 'UnicodeDecodeError'
node = tagger.parseToNode(copiedText)
extracted_wordlist = []
hiragana_wordlist = []
while node:
    word = node.surface
    feature = node.feature
    feature_list = feature.split(",")
    
    # If 'feature' list has less than six columns, skip the process. (e.x. 名詞,普通名詞,一般,*,*,*)
    if len(feature_list) < 5:
        print(f"Skipped this node process. 'feature' has less than six columns.\nfeature: {feature} ")
        node = node.next

    # get general pos (partOfSpeech)
    pos = feature_list[0]
    # get detailed pos
    sub_pos = feature_list[1]
    # get word in kanji (chinese character)   
    try:
        root_kanji = feature_list[7]
    except (IndexError) as e:
        print(f'Failed to get word root because no word data was detected: (error: {e})')
        print(f"  word -> {word}, number of index of feature -> {len( feature_list )}, feature: {feature}")
        node = node.next
    
    
    # print(f"{feature}")
    

    # Filter out words (exclude alphabet, numerals, single character word and ancient kanji)
    if sub_pos == '数詞':
        print(f"{word} was excluded because it's a numeral({pos})")
         # Exclude the words from the wordlist
    elif pos == '助動詞':
        print(f"{word} was excluded because it's an Auxiliary verb({pos})")
    elif pos == "助詞":
        print(f"{word} was excluded because it's a particle({pos})")
    elif pos == "接尾辞":
        print(f"{word} was excluded because it's a suffix({pos})")
    elif pos == "接頭辞":
        print(f"{word} was excluded because it's a prefix({pos})")
    elif pos == "副詞" and len(word) == 1:
        print(f"{word} was excluded because it's a single character adverb({pos})")
    elif pos == "感動詞" and len(word) == 1:
        print(f"{word} was excluded because it's an interjection({pos})")
    elif pos in { '動詞', "形容詞", "形状詞" }  or sub_pos == '普通名詞':
        # Extract kanji and add it to wordlist (root_kanji is 7th item in feature is written in kanji always)
        extracted_wordlist.append(root_kanji)
        print("動詞、形容詞、形状詞、普通名詞")
    elif sub_pos == '固有名詞':
        print("固有名詞 ↓")
        extracted_wordlist.append(word)
    elif pos in ( '名詞', '接続詞', '副詞', '連体詞', "代名詞" ):
        print("名詞, or 接続詞 or 副詞 or 連体詞 or代名詞 ↓")
        extracted_wordlist.append(word)
    node = node.next # Move on to next node(word)



# Remove duplicate words from wordlist
unique_wordlist = exclude_duplicate_word(extracted_wordlist)
# print(f"英数字除外前\n{unique_wordlist}")
# Exclude alphabetical words
no_alphabet_wordlist = exclude_alphabet(unique_wordlist)
print(f"除外後\n{no_alphabet_wordlist}")

# Exclude empty strings
packed_wordlist = [ i for i in no_alphabet_wordlist if i != '' ]
no_stop_word_list = exclude_stop_words(packed_wordlist)
processed_wordlist = no_stop_word_list


# Convert words to romaji and append it to romaji_wordlist
kks = pykakasi.kakasi()
romaji_wordlist = []
for word in processed_wordlist:
    romaji = kks.convert(word)[0]['hepburn']
    romaji_wordlist.append(romaji)
    # print(romaji)
# Convert hepbuern romaji to original french romaji
romaji_wordlist = convert_romaji_to_french_phonetic(romaji_wordlist)
# print(f'romaji_wordlist: {romaji_wordlist}')

# Get definition of each word
definition_wordlist = []
for word in processed_wordlist:
    definition = GoogleTranslator(source='ja', target='fr').translate(word)
    definition_wordlist.append(definition)
# print(f'definition_wordlist: {definition_wordlist}')

# Convert Kanji to Hiragana
hiragana_wordlist = convert_kanji_to_hiragana(processed_wordlist)

print(f"抽出単語数: {len(processed_wordlist)}\n{processed_wordlist}")
print(f"ひらがな数: {len(hiragana_wordlist)}\n{hiragana_wordlist}")

# Put together word, romaji and definition in a list
final_output_wordlist = []
for i in range(len(processed_wordlist)):
    if hiragana_wordlist[i] == "":
        final_output_wordlist.append(f"{processed_wordlist[i]}    [ {romaji_wordlist[i]} ] {definition_wordlist[i]}")
    else:
        final_output_wordlist.append(f"{processed_wordlist[i]}    [ {hiragana_wordlist[i]} / {romaji_wordlist[i]} ] {definition_wordlist[i]}")

# Convert final_output_wordlist to the list that contains words separated with comma.
comma_separated_wordlist = []
for i in range(len(processed_wordlist)):
    comma_separated_wordlist.append(f"{processed_wordlist[i]},{hiragana_wordlist[i]},{romaji_wordlist[i]},{definition_wordlist[i]}")
# print(f"comma_separated_wordlist: {comma_separated_wordlist}")

# Convert one-dimensional list to two-dimensional list to save it as csv file
two_d_output_wordlist = [ [i] for i in comma_separated_wordlist ]
# print(two_d_output_wordlist)

# Store output as a csv file
with open(f'{TOKENIZER_PROJECT_DIRECTORY}/jp-word-list-{formatted_dt_now}.csv', 'w') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_NONE, escapechar=" ")
    # writer.writerow(two_d_output_wordlist) # Use this line when writing a line into csv file
    writer.writerows(two_d_output_wordlist)

# Copy final output to the clipboard with a new line(\n) at the end of each word
final_output_string = '\n'.join(final_output_wordlist)
pyperclip.copy(final_output_string)