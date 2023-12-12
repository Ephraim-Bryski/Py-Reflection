from latex import latexify

"""
from source:


need to
    replace u.feet and foot with ft
    sub all vars in source code
    convert to latex
    combine to create b=3*i*ft=3*1*ft=3*ft


"""

unit_map = {

    "foot": "ft"
}


def add_line_to_word(doc, line, is_math):

    run = doc.add_paragraph().add_run(text=line)
    
    if is_math:
        run.font.math = True
        run.style.quick_style = True


def modify_unit(value):
    
    boop = value.split(" ")


    if len(boop) != 2:
        return value
    
    [value, unit] = boop



    if unit not in unit_map.keys():
        return value

    new_unit = unit_map[unit]

    return f"{value}*{new_unit}"


def split_by_ops(expression):

    expression = expression.replace(" ","")

    is_part_of_val = lambda char : char.isalnum() or char == "_" or char == "."

    val = ""

    stuff = []

    # this is just so it's a single char
    expression = expression.replace("**","^")

    for char in expression:
        
        if is_part_of_val(char):
            val += char
        else:
            if char == "^": char = "**"
            stuff.append(val)
            stuff.append(char)
            val = ""

    stuff.append(val)


    return stuff
    

def construct_line(line_meta):

        
    values = line_meta["values"]
    for key in values:
        values[key] = modify_unit(values[key])
        
    line = line_meta["source_code"]


    # im pretty sure i wrote it somewhere: "a*b" --> ["a","*","b"]

    # TODO TEMPORARY FIX
    DOT = "__DOT__"
    line = line.replace(".",DOT)

    [assign_var, assignment] = line.replace(" ","").split("=")

    final_value = values[assign_var]

    items = split_by_ops(assignment)

    subbed_items = items.copy()


    for idx, item in enumerate(subbed_items):

        if item not in values.keys():
            continue

        subbed_item = values[item]

        subbed_items[idx] = subbed_item


    subbed_line = "".join(subbed_items)

    single_value = len(values.keys()) == 1

    if single_value:
        full_line = f"{assign_var} = {final_value}"
    else:
        full_line = f"{assign_var} = {assignment} = {subbed_line} = {final_value}"


    latex_line = " = ".join(list(map(latexify,full_line.split("="))))

    latex_line = latex_line.replace(DOT,".")

    return latex_line

