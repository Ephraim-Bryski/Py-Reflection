# will have to merget this stuff with the insert code i wrote later
    # the some to insert code i could get rid of
    # the stuff for constructing latex, inserting into word, checking if it's math etc., i'll keep

import ast
import copy
from latex import latexify
from msword_gen import add_math_to_word
from typing import Callable

def find_trees_to_modify(tree, modifications: list):

    """
    no return just mutates modifications by adding trees attribute
    """

    def get_tree_string(tree):
        return ast.unparse(tree).replace('"',"").replace("'","")
        

    def search_down_tree(tree, prev_tree):
        
        correct_element = prev_tree is not None and get_tree_string(prev_tree) in labels
        
        if correct_element:
        
            index = labels.index(get_tree_string(prev_tree))
            modification = modifications[index]  
            modification.tree = tree

        if "body" not in tree.__dict__:
            # this does NOT work if the thing you're looking for isn't in something that has a body (e.g. an expression)
            return 
        
        subtrees = tree.body

        for i in range(len(subtrees)):

            subtree = subtrees[i]
            if i==0:
                prev_subtree = None
            else:
                prev_subtree = subtrees[i-1] 

            # modify this loop to get the previous one
            search_down_tree(subtree, prev_subtree)

    labels = list(map(lambda x:(x.label), modifications))

    search_down_tree(tree, None)

def is_math_line(line):

    # TODO i probably dont need to do this
    # i get all the values, so i just need to check whether they're numbers or units
    # much better cause something like a+b where they're both strings would show up as a math line

    # more copy pastinggggggggggggggggggg :)
    # it's fineeeeeeeeeee im lazy
    UNARY_OPS = (ast.UAdd, ast.USub)
    BINARY_OPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow)

    def is_arithmetic(s):
        def _is_arithmetic(node):
            if isinstance(node, ast.Num):
                return True
            elif isinstance(node, ast.Name):
                return True
            elif isinstance(node, ast.Expression):
                return _is_arithmetic(node.body)
            elif isinstance(node, ast.UnaryOp):
                valid_op = isinstance(node.op, UNARY_OPS)
                return valid_op and _is_arithmetic(node.operand)
            elif isinstance(node, ast.BinOp):
                valid_op = isinstance(node.op, BINARY_OPS)
                return valid_op and _is_arithmetic(node.left) and _is_arithmetic(node.right)
            else:
                raise ValueError('Unsupported type {}'.format(node))

        try:
            return _is_arithmetic(ast.parse(s, mode='eval'))
        except (SyntaxError, ValueError):
            return False


    if not isinstance(line, ast.Assign):
        return False 
    
    assign_vars = line.targets
    if len(assign_vars) != 1:
        raise False

    expression = ast.unparse(line.value)

    return is_arithmetic(expression)

def eqn_tree_to_latex(tree):

    assign_var = ast.unparse(tree.targets[0])
    expression = ast.unparse(tree.value)

    return f"{assign_var} = {latexify(expression)}"



with open("sample_calcs.py") as f:
    code = f.read()



from dataclasses import dataclass

@dataclass
class TreeModify:
    label: str
    insertion_function: Callable
    file_name: str = None # needed just when there's modules also with labels, AND if there's the same label name across different files
    iterator_selector: Callable = None# this would only be relevant for a for loop
    tree = None # some ast body type, gets added in search tree

GENERATED_DIR = "Generated"
GLOBAL_LATEX_VAR = "GLOBAL_LATEX"

# obviously these are themselves global variables in here, but by global i mean they're global in the modified code
# globallists is a list, but i mean that it contains variable names that would be assigned to lists in the modified code
GLOBAL_LISTS = [GLOBAL_LATEX_VAR] # for when i want more, e.g. excel
LATEX_ASSIGN_VAR = "LATEX_ASSIGN"






def insert_latex(line):
    
    # this could be passed into any modify function (e.g. modify_for_loop), then called in that function

    if not is_math_line(line):    
        return None

    eqn = eqn_tree_to_latex(line)

    assign_var = line.targets[0].id

    new_assignment = f'{LATEX_ASSIGN_VAR}="{eqn} = "+str({assign_var})'
    new_append = f'{GLOBAL_LATEX_VAR}.append({LATEX_ASSIGN_VAR})'
    
    return [ast.parse(new_assignment), ast.parse(new_append)]



def modify_for_loop(for_tree, insertion_function, iterator_selector):

    if iterator_selector == None:
        get_first_iteration = lambda x:(x[0])
        iterator_selector = get_first_iteration



    assert isinstance(for_tree, ast.For), "can only modify a for loop"

    base_if_tree = ast.parse("if True: pass").body[0] # just a placeholder, doing ast.If() leads to missing attributes

    iterator_variable = for_tree.target.id
    iterator = for_tree.iter
    iterator_values = list(eval(ast.unparse(iterator)))
    iterator_selected_value = iterator_selector(iterator_values)
    conditional_text = f"{iterator_variable} == {iterator_selected_value}"
    condition = ast.parse(conditional_text).body[0].value

    base_if_tree.test = condition

    new_for_bodies = []

    for line in for_tree.body:
        
        new_for_bodies.append(line)

        inserted_lines = insertion_function(line)

        if inserted_lines is None:
            continue # better than returning pass tree, so it doesnt fill it up with too much code

        if_tree = copy.deepcopy(base_if_tree)    

        if_tree.body = inserted_lines

        new_for_bodies.append(if_tree)

    for_tree.body = new_for_bodies


    # would need
        # the iterator index or condition on it
        # the tree, assert that it's a for body
        # what insertion to do, this would be a function
    # the insertion function would return a list of bodies
        # for this for loop modify, the for loop bodies would be assigned to this
        # it would take teh line of code as an input


def modify_code(file_name, modifications):
    
    # for now assume there's no imports

    with open(file_name) as f:
        tree = ast.parse(f.read())

    for global_var in GLOBAL_LISTS:
        tree.body.insert(0, ast.parse(f"{global_var} = []"))



    find_trees_to_modify(tree, modifications)

    for modification in modifications:
        assert isinstance(modification.tree, ast.For), "for now only allowing modification of for loops -- maybe add more flexibility?"


        # TODO write a function that returns the correct modifier function 
        # for now im just gonna assume im only modifying for loops

        modify_for_loop(\
            modification.tree,\
            modification.insertion_function,\
            modification.iterator_selector
        )

    new_code = ast.unparse(tree)

    with open("BOOOP.py","w") as f:
        f.write(new_code)
    # should then return dictionary with the subtrees for each label
    # they would be references to things in the main tree, so i can just mutate them directly


    global_output = {}
    exec(new_code, global_output)

    keys = copy.copy(list(global_output.keys()))

    for key in keys:
        if key not in GLOBAL_LISTS:
            del global_output[key]

    return global_output




file_name = "sample_calcs.py"
modifications = [
    TreeModify("MY MOD", insert_latex)
]


output = modify_code(file_name, modifications)

add_math_to_word("test.docx", output[GLOBAL_LATEX_VAR])
