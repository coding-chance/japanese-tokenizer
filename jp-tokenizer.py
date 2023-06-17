import pyperclip
import csv
import datetime
import MeCab
import re
from dotenv import load_dotenv
import os
import sys

# load environment variable set in .env
load_dotenv()
# Load directory path to the project directory from .env file
TOKENIZER_PROJECT_DIRECTORY = os.environ['TOKENIZER_PROJECT_DIR']

# Get current time info
dt_now = datetime.datetime.now()
formatted_dt_now = dt_now.strftime('%d-%m-%Y_%H-%M-%S')

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
    pos = feature.split(",")[0]
    sub_pos = feature.split(",")[1]
    # print(word)
    # print(feature)

    # Extract noun except numerals
    if pos == '数詞' or sub_pos == '固有名詞':
        print(f'{word} was excluded because it is a numeral or a proper noun')
         # Do nothing
    elif pos == '動詞':
        original_form_word = feature.split(",")[7]
        extracted_wordlist.append(original_form_word)
    elif pos in ( '名詞', '代名詞', '接続詞', '形容詞', '形状詞', '助詞', '助動詞', '副詞', '感動詞', '接頭辞', '接尾辞', '連体詞' ):
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


final_output_wordlist = no_single_character_wordlist
# print(f"output:\n{final_output_wordlist}")

# Convert one-dimensional list to two-dimensional list to save it as csv file
two_d_output_wordlist = [ [i] for i in final_output_wordlist ] 

# Store output as a csv file
with open(f'{TOKENIZER_PROJECT_DIRECTORY}/csv/jp-word-list-{formatted_dt_now}.csv', 'w') as f:
    writer = csv.writer(f)
    # writer.writerow(two_d_output_wordlist) # Use this line when writing a line into csv file
    writer.writerows(two_d_output_wordlist)

# Copy final output to the clipboard with a new line(\n) at the end of each word
final_output_string = '\n'.join(final_output_wordlist)
pyperclip.copy(final_output_string)