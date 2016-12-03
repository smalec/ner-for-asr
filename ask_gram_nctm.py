import configparser
import getopt
import re
import sys

from urllib.request import Request, urlopen


def nctm_to_xml(nctm_path):
    with open(nctm_path, 'r', encoding="utf-8") as f:
        xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<richText>'
        for line in f:
            simplified_line = re.sub('\|.*?\|', '', line)
            xml += '<paragraphs>' + simplified_line[:-1] + '</paragraphs>\n'
        xml += '</richText>'
    return xml.encode()


def ask_gram_textphrases(xml):
    config = configparser.ConfigParser()
    config.read("params.ini")
    req = Request(
        url=config["Gram"]["url"] + "textphrases",
        data=xml,
        headers={'Content-Type': 'application/xml', "Accept": 'application/json'}
    )
    return urlopen(req).read()


if __name__ == "__main__":
    input_nctm = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:", ["input_nctm="])
    except getopt.GetoptError:
        print("Usage: ask_gram_nctm.py -i test.txt")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-i":
            input_nctm = arg
    print(ask_gram_textphrases(nctm_to_xml(input_nctm)))
