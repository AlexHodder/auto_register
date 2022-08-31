import xml.etree.cElementTree as ET


def get_value(key, tree: ET.ElementTree):
    return tree.find(TRANSLATE_DICT[key]).text.strip()


TRANSLATE_DICT = {'First name': 'firstname',
                  'Last name': 'lastname',
                  'Full name': 'fullname',
                  'Country': 'country',
                  'Age': 'age',
                  'Date of birth': 'date-of-birth',
                  'Region': 'region',
                  'Username': 'username-base',
                  'Password': 'password',
                  'Phone number': 'mobile-number',
                  'Email Address': 'email',
                  'Postcode': 'postcode'}
