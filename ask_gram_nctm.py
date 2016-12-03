import configparser
import getopt
import re
import sys

from urllib.request import Request, urlopen


def nctm_to_xml(nctm_path):
    with open(nctm_path, 'r', encoding="utf-8") as f:
        xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<richText>'
        timestamps = []
        for line in f:
            line_timestamps = []
            for timestamp in re.findall('\|.*?\|', line):
                line_timestamps.append(timestamp[1:-1])
            timestamps.append(line_timestamps)
            simplified_line = re.sub('\|.*?\|', '', line)
            xml += '<paragraphs>' + simplified_line[:-1] + '</paragraphs>\n'
        xml += '</richText>'
    return xml.encode(), timestamps


def ask_gram_textphrases(xml):
    config = configparser.ConfigParser()
    config.read("params.ini")
    req = Request(
        url=config["Gram"]["url"] + "textphrases",
        data=xml,
        headers={'Content-Type': 'application/xml', "Accept": 'application/json'}
    )
    return urlopen(req).read()


def get_annotated_phrases(gram_response, timestamps):
    response_dict = eval(gram_response)
    result = {}
    for paragraph, line_timestamps in zip(response_dict["paragraphs"], timestamps):
        for phrase in paragraph["phrases"]:
            if phrase["@type"] == "atomPhrase" and phrase["atom"]["leftWhite"] == "true":
                del line_timestamps[:2]
            if phrase["@type"] == "annotatedPhrase":
                if type(phrase["phrases"]) == list:
                    count_phrases = len([1 for inner_phrase in phrase["phrases"] if inner_phrase["@type"] != "whitePhrase"])
                else:
                    count_phrases = 1
                if phrase["annotation"]["phraseType"]["$"] == "Person":
                    phrase["start"], phrase["end"] = line_timestamps[0], line_timestamps[2*count_phrases - 1]
                    if type(phrase["phrases"]) == list:
                        joined_phrase = ""
                        for inner_phrase in phrase["phrases"]:
                            joined_phrase += inner_phrase["whites"] if "whites" in inner_phrase else inner_phrase["atom"]["text"]
                        result[(line_timestamps[0], line_timestamps[2 * count_phrases - 1])] = joined_phrase
                    else:
                        result[(line_timestamps[0], line_timestamps[2*count_phrases - 1])] = phrase["atom"]["text"]
                del line_timestamps[:2*count_phrases]
    return result


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

    request, timestamps = nctm_to_xml(input_nctm)
    response = ask_gram_textphrases(request)
    print(get_annotated_phrases(response, timestamps))
