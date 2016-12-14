import configparser
import getopt
import re
import sys

from urllib.request import Request, urlopen

NONLETTERS = "[^a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]"


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
            xml += '<paragraphs>' + re.sub("&", "&#038;", simplified_line)[:-1] + '</paragraphs>\n'
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


def get_joined_phrase(phrases):
    if type(phrases) != list:
        phrases = [phrases]
    joined_phrase = ""
    for inner_phrase in phrases:
        if inner_phrase["@type"] == "whitePhrase":
            joined_phrase += inner_phrase["whites"]
        elif inner_phrase["@type"] == "atomPhrase":
            joined_phrase += inner_phrase["atom"]["text"]
        elif inner_phrase["@type"] == "annotatedPhrase":
            joined_phrase += get_joined_phrase(inner_phrase["phrases"])
        else:
            raise Exception("Unknown phrase type")
    return joined_phrase


def get_annotated_phrases(gram_response, timestamps):
    response_dict = eval(gram_response) if gram_response != b'null' else {"paragraphs": []}
    result = {}
    if type(response_dict["paragraphs"]) != list:
        response_dict["paragraphs"] = [response_dict["paragraphs"]]
    for paragraph, line_timestamps in zip(response_dict["paragraphs"], timestamps):
        remove_next = True
        if type(paragraph["phrases"]) == list:
            for phrase in paragraph["phrases"]:
                if phrase["@type"] == "atomPhrase":
                    if re.sub(NONLETTERS, "", phrase["atom"]["text"]):
                        if remove_next:
                            del line_timestamps[:2]
                        else:
                            if phrase["atom"]["rightWhite"] == "true" or phrase["atom"]["leftWhite"] == "true":
                                remove_next = True
                    else:
                        if phrase["atom"]["rightWhite"] == "false" and phrase["atom"]["leftWhite"] == "false":
                            remove_next = False
                        if phrase["atom"]["rightWhite"] == "true" and phrase["atom"]["leftWhite"] == "true":
                            del line_timestamps[:2]
                if phrase["@type"] == "annotatedPhrase":
                    joined_phrase = get_joined_phrase(phrase["phrases"])
                    count_phrases = len(joined_phrase.split())
                    if phrase["annotation"]["phraseType"]["$"] == "Person":
                        phrase["start"], phrase["end"] = line_timestamps[0], line_timestamps[2*count_phrases - 1]
                        result[str((line_timestamps[0], line_timestamps[2*count_phrases - 1]))] = joined_phrase
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
