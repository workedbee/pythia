import sys
import json
import locale
import codecs
import datetime
from os import path
from http import load_html_page
from parse import parse_leon_bet_html

work_directory = path.dirname(path.abspath(__file__))
# work_directory = 'C:\\Users\\workedbee\\Desktop\\bets\\liga_stavok\\'


def main():
    locale.setlocale(locale.LC_ALL, 'RUS')
    get_leon_bets_history()


def get_leon_bets_history():
    data = load_html_page("https://www.leon.ru/betoffer/10000004/10560", {})
    lines = parse_leon_bet_html(data)

    print lines

    # file_name = 'Basketball_1800_{}.txt'.format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    # file_name = work_directory + file_name
    # with open(file_name, "w") as text_file:
    #     text_file.write(data)

if __name__ == "__main__":
    main()