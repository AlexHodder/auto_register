from uiautomator import device as d
import parse_dump
import xml.etree.cElementTree as ET
import helper
import argparse
parser = argparse.ArgumentParser(description='Process package name')
parser.add_argument('--package', type=str, help='pass package name')
args = parser.parse_args()

d.dump('dump.xml', True, True)

package_name = args.package
input_tree = ET.parse('input_values.xml')


def fill_current(edit_text_dict, box_dict, button_dict, clickable_dict):
    for key in edit_text_dict.keys():
        print(f'Setting {key} field \n -----------------')

        d(className='android.widget.EditText', text=edit_text_dict[key]['text'],
          description=edit_text_dict[key]['content-desc']).set_text(helper.get_value(key, input_tree))

        # Click and select focused method -- doesn't currently work due to bounds
        # being used to click and keyboard causing issues

        # bound = edit_text_dict[key].get('bounds')
        # print(key)
        # x, y = parse_dump.centre_point(*parse_dump.bounds_to_int(bound))
        # d.click(x, y)
        # d.press('back')
        # d(focused=True, className='android.widget.EditText').set_text(f'SELECTED {key}')
    d.press.back()

    for key in box_dict.keys():
        print(f'Setting {key} checkbox to True')
        box = d(className='android.widget.CheckBox', text=box_dict[key]['text'],
                description=box_dict[key]['content-desc'])
        # box.click()
        if box_dict[key]['checked'] == 'false':
            box.click()

    before = d.dump()
    # from here it's likely that the screen will change
    active = True

    # Click each button - currently disabled
    # for key in button_dict.keys():
    #     print(f'Pressing button {key}.')
    #     button = d(className='android.widget.Button', text=button_dict[key]['text'],
    #                description=button_dict[key]['content-desc'])
    #     button.click()
    #     after = d.dump()
    #     # ensure that if the activity or screen drastically changes, we halt the program else we get exceptions
    #     if before != after:
    #         active = False
    #         print('layout changed - breaking loop')
    #         break

    # Click each item in the view - currently disabled
    # if active:
    #     for item in clickable_dict.keys():
    #         print(f'Clicking clickable view {item} of class {clickable_dict[item].get("class")}')
    #         clickable_item = d(className=clickable_dict[item].get('class'),
    #                            resourceId=clickable_dict[item].get('resource-id'),
    #                            text=clickable_dict[item].get('text'),
    #                            description=clickable_dict[item].get('content-desc'))
    #         clickable_item.click()
    #         after = d.dump()
    #         # ensure that if the activity or screen drastically changes, we halt the program else we get exceptions
    #         if before != after:
    #             active = False
    #             break
    #     return active


# Place holder function to eventually be used as the end-to-end system
def main():
    # need a method of understanding that registration is complete
    while True:
        fill_current(*parse_dump.get_attributes_to_fill('dump.xml', package_name=package_name))


fill_current(*parse_dump.get_attributes_to_fill('dump.xml', package_name=package_name))
d.dump(f'{package_name}.xml')
d.screenshot(f'{package_name}_filled.png')
