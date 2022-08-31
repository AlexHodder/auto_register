import argparse
import xml.etree.cElementTree as ET
import os
import re
from natsort import natsorted

def find_login(directory_path):
    step_dict = {}
    paths = os.listdir(directory_path)
    for filename in natsorted(paths):
        if filename.endswith('.xml'):
            full_path = os.path.join(directory_path, filename)
            # print(full_path)
            tree = ET.parse(full_path)
            root = tree.getroot()
            score = 0
            for child in root.iter():
                text = child.get('text').lower()
                obj_class = child.get('class').lower()
                content_desc = child.get('content-desc').lower()
                package = child.get('package').lower()
                # print(text, obj_class, content_desc, package)
                matching_text = ['login', 'log in', 'sign in']
                for keyword in matching_text:
                    if text.__contains__(keyword) or content_desc.__contains__(keyword):
                        score = 1
            step_dict[filename] = score
    print(step_dict)


def find_create_acc(directory_path):
    step_dict = {}
    paths = os.listdir(directory_path)
    print(directory_path)
    for filename in natsorted(paths):
        if filename.endswith('.xml'):
            full_path = os.path.join(directory_path, filename)
            tree = ET.parse(full_path)
            root = tree.getroot()
            score = 0
            for child in root.iter():
                text = child.get('text').lower()
                obj_class = child.get('class').lower()
                content_desc = child.get('content-desc').lower()
                package = child.get('package').lower()
                # print(text, obj_class, content_desc, package)

                matching_text = ['create account', 'sign up', 'create an account', 'create new account', 'register']
                for keyword in matching_text:
                    if text.__contains__(keyword) or content_desc.__contains__(keyword):
                        score = 1
                        # if child.get('clickable')=="true":
                            # begin register process
            step_dict[filename] = score

    for key in step_dict:
        if step_dict[key]:
            print(key, step_dict[key])


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description="Argument parser")
    # parser.add_argument('--dirpath', type=str)
    # args = parser.parse_args()
    # dirpath = args.dirpath
    find_login('/home/alex/Documents/SummerProject/ape_new_comp_test/sata-com.firstgroup.first.bus-ape-sata-running-minutes-5')
    find_create_acc('/home/alex/Documents/SummerProject/ape_new_comp_test/sata-com.firstgroup.first.bus-ape-sata-running-minutes-5')

    # find_create_acc(
    #     '/home/alex/Documents/SummerProject/Ape/prelim-apps/insta-out/sata-com.instagram.android-ape-sata-running-minutes-5')
    # find_create_acc(
    #     '/home/alex/Documents/SummerProject/Ape/prelim-apps/bbc-out/sata-bbc.mobile.news.uk-ape-sata-running-minutes-10')
    # find_create_acc(
    #     '/home/alex/Documents/SummerProject/Ape/prelim-apps/shareit-out/sata-com.lenovo.anyshare.gps-ape-sata-running-minutes-10')

    # See PyCharm help at https://www.jetbrains.com/help/pycharm/
