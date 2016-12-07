import configparser
import json
import os

from ask_gram_nctm import *


def run_single(nctm):
    request, timestamps = nctm_to_xml(nctm)
    response = ask_gram_textphrases(request)
    return get_annotated_phrases(response, timestamps)


def run(dir_path, output_dir):
    for (path, dirs, files) in os.walk(dir_path):
        for dir_ in dirs:
            os.makedirs(os.path.join(os.path.join(output_dir, path.lstrip(dir_path)), dir_), exist_ok=True)
        for file_ in files:
            if file_.endswith("_aligned.txt"):
                file_full_path = os.path.join(path, file_)
                file_relative_path = os.path.join(path.lstrip(dir_path), file_)
                file_output_path = os.path.join(output_dir, file_relative_path[:-12] + ".json")
                file_already_exists = os.path.isfile(file_output_path)
                if not file_already_exists:
                    gram_output = run_single(file_full_path)
                    json.dump(gram_output, file_output_path)
                    print("Retrived {}".format(file_full_path))


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("params.ini")
    run(config["Ascope"]["aligned_dir"], config["Ascope"]["gram_outputs_dir"])
