# of course don't just have this floating around, will be part of something else

import ast






# 'a * b' --> 'str(a) + "*" + str(b)'
# just do string manimpulation

import pint

def construct_valued_expression(expression):

    is_part_of_val = lambda char : char.isalnum() or char == "_" or char == "."

    val = ""
    new_text = ''

    expression = expression.replace("**","^")

    #expression += " " # allows it to append to last value

    for char in expression:
        
        if is_part_of_val(char):
            val += char
        else:
            new_text += f'str({val})+'
            new_text += f'"{char}"'
            val = ""

    new_text += f'str({val})'

    new_text = new_text.replace("^","**")

    return new_text
    


boop = construct_valued_expression("a**b")
pass