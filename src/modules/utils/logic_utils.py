import re
import string


###################################################################
#  String Logic
###################################################################

def removeIllegalCharacters(input_string):
    # Define a regular expression pattern to match illegal and escape characters
    pattern = r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]'

    # Use re.sub to replace matched characters with an empty string
    cleaned_string = re.sub(pattern, '', input_string)

    return cleaned_string

def remove_control_characters(text):
    # Create a translation table that maps control characters to None
    control_chars = dict.fromkeys(range(32))  # ASCII values 0-31
    control_chars[127] = None                 # Also include DEL character (ASCII 127)
    return text.translate(control_chars)

def remove_unicode_characters(text):
    # Create a translation table with all Unicode characters set to None
    translation_table = dict.fromkeys(range(0x10000), None)
    translation_table.update(str.maketrans("", "", string.printable))

    # Remove Unicode characters using the translation table
    cleaned_text = text.translate(translation_table)

    return cleaned_text

###################################################################
#  Math Logic
###################################################################

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def is_real_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def hardnessCalc(calcium, magnesium, dilution):
    calcium = float(calcium) * float(dilution)
    magnesium = float(magnesium) * float(dilution)

    return round(calcium * 2.497 + calcium * 4.11, 1)

###################################################################
#  Lists Logic
###################################################################

def search_list_of_lists(lists, targets):
    for sublist in lists:
        if all(target in sublist for target in targets):
            return sublist
    return None