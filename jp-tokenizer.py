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

# Get current time info
dt_now = datetime.datetime.now()
formatted_dt_now = dt_now.strftime('%Y-%m-%d_%H.%M.%S')

# Get data stored in clipboard
copiedText = pyperclip.paste()

# Extract words
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
        print(f'No word data was detected: ({e})')
        print(f"word: {word}")
        print(f"feature: {feature}")
        print(f"number of index of feature: {len( feature_list )}")
        node = node.next
    
    print(feature)
    

    

    
    

    # Extract noun except numerals
    if pos == '数詞':
        print(f"{word} was excluded because it's a numeral({pos})")
         # Exclude the words from the wordlist
    elif sub_pos == '固有名詞':
        print(f"{word} was excluded because it's a proper noun({sub_pos})")
    elif pos == '助動詞':
        print(f"{word} was excluded because it's an Auxiliary verb({pos})")
    elif pos == "助詞":
        print(f"{word} was excluded because it's a particle({pos})")
    elif pos == "接尾辞":
        print(f"{word} was excluded because it's a suffix({pos})")
    elif pos in { '動詞', "形容詞", "形状詞" }  or sub_pos == '普通名詞':
        # Extract 7th item (kanji word) and add it to wordlist
        extracted_wordlist.append(root_kanji)
    elif pos in ( '名詞', '接続詞', '副詞', '感動詞', '接頭辞', '連体詞', "代名詞" ):
        extracted_wordlist.append(word)
    
    node = node.next # Move on to next node(word)


# Combine duplicate words into one.
no_duplicate_wordlist = []
for num in extracted_wordlist:
     if num not in no_duplicate_wordlist:
         no_duplicate_wordlist.append(num)
# ↓ Rewrite the code above using list comprehensions (内包表記)
# [ no_duplicate_wordlist.append(num) for num in extracted_wordlist if not num in no_duplicate_wordlist ] 



# Exclude alphabetical words
japanese = re.compile('[ぁ-んァ-ン一-龥]+')
no_alphabet_wordlist = []
for word in no_duplicate_wordlist:
    if japanese.findall(word):
        no_alphabet_wordlist.append(word)

# Exclude empty strings
no_empty_string_wordlist = [ i for i in no_alphabet_wordlist if i != '' ]
# print(no_empty_string_wordlist)

# Exclude single-character katakana and hiragana
no_single_character_wordlist = []
reg_hiragana = re.compile(r'^[あ-ん]+$')
reg_katakana = re.compile(r'[\u30A1-\u30F4]+')
for word in no_empty_string_wordlist:
    if reg_hiragana.fullmatch(word) != True and reg_katakana.fullmatch(word) != True and len(word) != 1:
        no_single_character_wordlist.append(word)
    # print(f'{word} is hiragana?: {reg_hiragana.fullmatch(word)}')
    # print(f'{word} is katakana?: {reg_katakana.fullmatch(word)}')
    # print(f'length of {word}: {len(word)}')




# Convert words to romaji and append it to romaji_wordlist
kks = pykakasi.kakasi()
romaji_wordlist = []
for word in no_single_character_wordlist:
    romaji = kks.convert(word)[0]['hepburn']
    romaji_wordlist.append(romaji)
    # print(romaji)



# Get definition of each word
definition_wordlist = []
for word in no_single_character_wordlist:
    definition = GoogleTranslator(source='ja', target='fr').translate(word)
    definition_wordlist.append(definition)
# print(f'definition_wordlist: {definition_wordlist}')

# Put together word, romaji and definition in a list
final_output_wordlist = []
for i in range(len(no_single_character_wordlist)):
    final_output_wordlist.append(f"{no_single_character_wordlist[i]}    [{romaji_wordlist[i]}] {definition_wordlist[i]}")

# Convert final_output_wordlist to the list that contains words separated with comma.
comma_separated_wordlist = []
for i in range(len(no_single_character_wordlist)):
    comma_separated_wordlist.append(f"{no_single_character_wordlist[i]},{romaji_wordlist[i]},{definition_wordlist[i]}")
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