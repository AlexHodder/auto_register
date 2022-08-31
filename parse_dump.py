import xml.etree.cElementTree as ET
import re
import torch
from sentence_transformers import SentenceTransformer, util
import math
import helper

model = SentenceTransformer('all-MiniLM-L6-v2')


# Function to load in uidump as a tree
def file_load_to_tree(path):
    return ET.parse(path)


input_sentences = list(helper.TRANSLATE_DICT.keys())
input_embeddings = model.encode(input_sentences, convert_to_tensor=True)

button_sentences = ['Confirm',
                    'Next',
                    'Sign Up',
                    'Create']
button_embeddings = model.encode(button_sentences, convert_to_tensor=True)


# function that searches the uidump to find the input requirements for the current ui
def get_attributes_to_fill(path, package_name):
    tree = file_load_to_tree(path)
    print("--------------------")
    print(package_name)

    root = tree.getroot()
    parent_map = {c: p for p in tree.iter() for c in p}

    package_root = root.find(f"./node/[@package='{package_name}']")

    edit_texts = get_edit_texts(package_root, parent_map)
    check_boxes = get_checkbox(package_root, parent_map)
    buttons = get_buttons(package_root, parent_map)
    clickables = get_other_clickable_views(package_root)

    print(f"Edit Texts: {edit_texts}\nCheckbox: {check_boxes}\nButtons: {buttons}\nClickables: {clickables}")

    return edit_texts, check_boxes, buttons, clickables


# Function to loop through tree and return all Checkbox's and their found context message
def get_checkbox(package_root, parent_map):
    query_sentences = []

    checkbox_items = []
    # Loop to find all Button views in the current view (and their corresponding input hint)
    for item in package_root.findall(".//node[@class='android.widget.CheckBox']"):
        text = item.get('text')
        content = item.get('content-desc')
        checkbox_items.append(item)

        # case for where input description is in the same layout view (only search same layer)
        if len(text) == 0 and len(content) == 0:
            parent_node = parent_map[item]
            found_context, text, content = move_up_layer(parent_node, item)
            if found_context:
                query_sentences.append(text) if text != '' else query_sentences.append(content)
        else:
            query_sentences.append(text) if text != '' else query_sentences.append(content)

    checkbox_output = {}
    for i in range(len(query_sentences)):
        checkbox_output[query_sentences[i]] = checkbox_items[i].attrib

    return checkbox_output


# Function to loop through tree and find all Buttons
def get_buttons(package_root, parent_map):
    query_sentences = []

    button_items = []
    # Loop to find all Button views in the current view (and their corresponding input hint)
    for item in package_root.findall(".//node[@class='android.widget.Button']"):
        text = item.get('text')
        content = item.get('content-desc')
        button_items.append(item)

        # case for where input description is in the same layout view (only search same layer)
        if len(text) == 0 and len(content) == 0:
            parent_node = parent_map[item]
            found_context, text, content = move_up_layer(parent_node, item)
            if found_context:
                query_sentences.append(text) if text != '' else query_sentences.append(content)
        else:
            query_sentences.append(text) if text != '' else query_sentences.append(content)

    button_output = {}
    # top = min(1, len(input_sentences))
    # for i in range(len(query_sentences)):
    #     query = query_sentences[i]
    #     query_embedding = model.encode(query, convert_to_tensor=True)
    #     cos_scores = util.cos_sim(query_embedding, input_embeddings)[0]
    #     top_results = torch.topk(cos_scores, k=top)
    #
    #     if top_results[0] > 0.5:
    #         print(f"{query} with score {top_results[0]} matching {input_sentences[top_results[1]]}")

    for i in range(len(query_sentences)):
        button_output[query_sentences[i]] = button_items[i].attrib

    return button_output


# Function to loop through screen and return all EditTexts and their found context message
def get_edit_texts(package_root, parent_map):
    query_sentences = []

    edit_text_items = []
    # Loop to find all EditText views in the current view (and their corresponding input hint)
    for item in package_root.findall(".//node[@class='android.widget.EditText']"):
        text = item.get('text')
        content = item.get('content-desc')
        edit_text_items.append(item)

        # case for where input description is in the same layout view but not in the same EditText (search two above
        # layers)
        if len(text) == 0 and len(content) == 0:
            parent_node = parent_map[item]
            found_context, text, content = move_up_layer(parent_node, item)
            if not found_context:
                found_context, text, content = move_up_layer(parent_map[parent_node], item)
            if found_context:
                query_sentences.append(text) if text != '' else query_sentences.append(content)
        else:
            query_sentences.append(text) if text != '' else query_sentences.append(content)

    edit_text_output = {}
    top = min(1, len(input_sentences))
    for i in range(len(query_sentences)):
        query = query_sentences[i]
        query_embedding = model.encode(query, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, input_embeddings)[0]
        top_results = torch.topk(cos_scores, k=top)

        if top_results[0] > 0.5:
            print(f"{query} with score {top_results[0]} matching {input_sentences[top_results[1]]}")
            edit_text_output[input_sentences[top_results[1]]] = edit_text_items[i].attrib

    return edit_text_output


def get_other_clickable_views(package_root):
    item_dict = {}
    for item in package_root.findall(".//node[@clickable='true']"):
        if item.get('class') not in ['android.widget.EditText', 'android.widget.Button', 'android.widget.CheckBox']:
            if item.get('text') == '':
                item_dict[item.get('content-desc')] = item.attrib
            else:
                item_dict[item.get('text')] = item.attrib
    return item_dict


def move_up_layer(parent_node: ET.Element, item: ET.Element):
    context = False
    edit_text_bounds = bounds_to_int(item.get('bounds'))
    final_text, final_content = '', ''
    closest_dist = 1000000
    for x in parent_node.findall('.//node'):
        text = x.get('text')
        content = x.get('content-desc')
        bounds = bounds_to_int(x.get('bounds'))

        if text != '' or content != '':
            overlap = is_overlapping(centre_point(*bounds), edit_text_bounds)
            # if text overlaps EditText assume it labels the EditText
            if overlap:
                return True, text, content
            dist = euclid_distance(centre_point(*edit_text_bounds), centre_point(*bounds))
            if dist < closest_dist:
                closest_dist = dist
                final_content = content
                final_text = text
                context = True

    return context, final_text, final_content


def bounds_to_int(bounds):
    group = re.search('[[]([0-9]+),([0-9]+)[]][[]([0-9]+),([0-9]+)[]]', bounds)
    x1 = group.group(1)
    y1 = group.group(2)
    x2 = group.group(3)
    y2 = group.group(4)
    return int(x1), int(y1), int(x2), int(y2)


def centre_point(x1, y1, x2, y2):
    return (x1 + x2) / 2, (y1 + y2) / 2


def is_overlapping(centre, overlapping_box):
    return (overlapping_box[0] < centre[0] < overlapping_box[2]) \
           and (overlapping_box[1] < centre[1] < overlapping_box[3])


def euclid_distance(centre_1, centre_2):
    return math.sqrt((centre_2[0] - centre_1[0]) ** 2 + (centre_2[1] - centre_1[1]) ** 2)

