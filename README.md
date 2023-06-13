# Japanese Tokenizer
This script extracts japanese words from a japanese text.
This is useful when you want to take words out of a huge text one by one.
Japanese teachers may find this script useful when creating student-specific vocabulary list.

If you run this programme while a japanese sentence is copied to the clipboard, words are extracted from the it and stored in the clipboard. Words other than hiragana, symbols and duplicate words are excluded.
 
For example, if you copy the following sentence and run the program...

```
明日もし晴れたら、私はショッピングに出かけるだろう。
```

You will have the following result. 

```
明日
もし
晴れ
たら
私
は
ショッピング
に
出かける
だろう
```

Did you notice we have a line break at the end of each word? This format makes it easy to paste words into spreadsheet applications like Excel.

<br>

## Prerequisites
Before start running this program, install the following dependencies
- [pyperclip](https://pypi.org/project/pyperclip/)
- [MeCab](https://github.com/SamuraiT/mecab-python3)
- [dotenv](https://pypi.org/project/python-dotenv/)

<br>

## How to run the program
0. Download all the files from this repository. You can also use `git clone` command to make it available the code on your computer.
```
git clone https://github.com/coding-chance/japanese-tokenizer
```

1. Make a directory called "csv" under the root directory of the project. The extracted japanese words will be stored in both this file. Of course, the word will be directly stored in your clipboard too.

2. Create a new file under the root directory and name it `.env` and write the path to the project directly. Modify `.env` like following.
```.env
TOKENIZER_PROJECT_DIR="copy/the/absolute/path/here/to/this/directory"
```

3. Copy the text from which you want to extract the Japanese.

4. Run the script on your terminal(mac/linux) or command prompt(windows).
```bash
python /path/to/project/directory/jp-tokenizer.py
```

5. Now your clipboard holds the extracted words. Paste it anywhere you want. The extracted words are also stored under `csv` directory so please use them if you need.

<br>

\* Send me a message if you had a problem. I might be able to help you out.
 
<br>

## Tips
If you're using macOS, you can run this script from spotlight search bar at any time by creating an app that runs this program on `automator`.
 
<br>

## Hints to understand the program
### Japanese words used in the code
- 数詞(すうし/Suushi): numeral
- 固有名詞(こゆうめいし/koyuumeishi): proper noun
- 名詞(めいし/meishi): noun
- 接続詞(せつぞくし/setsuzokushi): conjunction
- 動詞(どうし/doushi): verb
- 形容詞(けいようし/keiyoushi): adjective
- 助詞(じょし/joshi): particle
- 助動詞(助動詞/jodoushi): auxiliary verb
- 副詞(ふくし/fukushi): adverb
- 感動詞(かんどうし/kandoushi): interjection
- 接頭辞(せっとうじ/settouji): prefix
- 接尾辞(せつびじ/setsubiji): suffix

<br>

## Future Update
I am currently thinking to add a function to this application that allows users to have the furigana(ruby) for kanji words using [よみたんAPI](https://yomi-tan.jp/man/v1). 