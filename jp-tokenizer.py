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
    japanese = re.compile('[ぁ-んァ-ン一-龥]+')
    no_alphabet_wordlist = []
    for word in wordlist:
        if japanese.findall(word):
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
    
    if word in {"ユウ", "為る"} :
        print(f"{word}: {feature}")
    

    # Filter out words (exclude single character word and numerals)
    if pos == '数詞':
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
    elif pos in { '動詞', "形容詞", "形状詞" }  or sub_pos == '普通名詞':
        # Extract kanji and add it to wordlist (root_kanji is 7th item in feature is written in kanji always)
        extracted_wordlist.append(root_kanji)
    elif sub_pos == '固有名詞':
        extracted_wordlist.append(word)
    elif pos in ( '名詞', '接続詞', '副詞', '感動詞', '連体詞', "代名詞" ):
        extracted_wordlist.append(word)

    node = node.next # Move on to next node(word)




# Remove duplicate words from wordlist
unique_wordlist = exclude_duplicate_word(extracted_wordlist)
# Exclude alphabetical words
no_alphabet_wordlist = exclude_alphabet(unique_wordlist)
# Exclude empty strings
packed_wordlist = [ i for i in no_alphabet_wordlist if i != '' ]
# print(packed_wordlist)
processed_wordlist = packed_wordlist


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

# Put together word, romaji and definition in a list
final_output_wordlist = []
for i in range(len(processed_wordlist)):
    final_output_wordlist.append(f"{processed_wordlist[i]}    [ {romaji_wordlist[i]} ] {definition_wordlist[i]}")

# Convert final_output_wordlist to the list that contains words separated with comma.
comma_separated_wordlist = []
for i in range(len(processed_wordlist)):
    comma_separated_wordlist.append(f"{processed_wordlist[i]},{romaji_wordlist[i]},{definition_wordlist[i]}")
# print(f"comma_separated_wordlist: {comma_separated_wordlist}")

# Convert one-dimensional list to two-dimensional list to save it as csv file
two_d_output_wordlist = [ [i] for i in comma_separated_wordlist ]
# print(two_d_output_wordlist)

# Store output as a csv file
with open(f'{TOKENIZER_PROJECT_DIRECTORY}/csv/jp-word-list-{formatted_dt_now}.csv', 'w') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_NONE, escapechar=" ")
    # writer.writerow(two_d_output_wordlist) # Use this line when writing a line into csv file
    writer.writerows(two_d_output_wordlist)

# Copy final output to the clipboard with a new line(\n) at the end of each word
final_output_string = '\n'.join(final_output_wordlist)
pyperclip.copy(final_output_string)


