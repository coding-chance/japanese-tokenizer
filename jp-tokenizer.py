# 日本語の単語を抽出するプログラム

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


# Use the following lines when you want the program to wait for copying a new string
# try:
#     print("Copy the target text (timeout 60 seconds)")
#     newCopiedText = pyperclip.waitForNewPaste(60)
#     print(f"Copied Text: {newCopiedText}")
# except pyperclip.PyperclipTimeoutException:
#     print("Exit process due to timeout")
#     sys.exit()


# Extract words
tagger = MeCab.Tagger()
tagger.parse("") # To avoid 'UnicodeDecodeError'
node = tagger.parseToNode(copiedText)
extracted_wordlist = []
while node:
    word = node.surface
    feature = node.feature
    part = feature.split(",")[0]
    sub_part = feature.split(",")[1]

    # Extract noun except numerals
    if part == '数詞' or sub_part == '固有名詞':
        print(f'{word} was excluded because it is a numeral or a proper noun')
         # Do nothing
    elif part in ( '名詞', '代名詞', '接続詞', '動詞', '形容詞', '助詞', '助動詞', '副詞', '感動詞', '接頭辞', '接尾辞' ):
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

final_output_wordlist = no_empty_string_wordlist
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