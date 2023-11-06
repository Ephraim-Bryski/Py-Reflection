
import inspect
import ast
import copy
import re


import sample


functions_to_insert = [sample.outer, sample.inner]



OPTIONAL_OUTPUT_NAME = "__OPTIONAL_OUTPUT__"
INSERTION_FUNCTIONS_VAR_NAME = "__INSERTION_FUNCTIONS__"
INSERTIONS_NAME = "__INSERTIONS__"





def get_top_functions(tree):
    
    def is_function(subtree):
        return isinstance(subtree, ast.FunctionDef)
    

    functions = filter(is_function, tree.body)

    return list(functions)


def extract_variables(equation):
    # hack i added so that functions won't be included as variables (things with periods won't count and parentheses)
    DUMMY = "__DUMMY_DONT_INCLUDE__"
    equation = equation.replace(".",DUMMY).replace("(",DUMMY)
    # chatgpt code, i hate regexes
    # Regular expression pattern to match variables (assuming variable names contain letters and/or numbers)
    pattern = r'[a-zA-Z_][a-zA-Z0-9_]*'
    variables = re.findall(pattern, equation)
    variables = filter(lambda x: (DUMMY not in x), variables)
    return list(set(variables))


def modify_function_call(items, assignment, new_insertion):
    
    function_assignment = assignment

    def copy_tree(tree): return ast.parse(ast.unparse(tree)).body[0]

    modified_function_assignment = copy_tree(function_assignment) # could have just unparsed and thenunparsed
    
    output = ast.unparse(modified_function_assignment.targets[0])

    modified_output = f'[{output}, {OPTIONAL_OUTPUT_NAME}]'

    modified_function_assignment.targets[0] = ast.parse(modified_output).body[0].value

    modified_function_call = modified_function_assignment.value

    func_name = modified_function_call.func

    new_keyword = ast.keyword()

    new_keyword.arg = INSERTION_FUNCTIONS_VAR_NAME
    new_keyword.value = ast.parse(INSERTION_FUNCTIONS_VAR_NAME).body[0].value
        

    modified_function_call.keywords.append(new_keyword)


    branch_call_text = \
f"""if {INSERTION_FUNCTIONS_VAR_NAME} is not None and {ast.unparse(func_name)} in {INSERTION_FUNCTIONS_VAR_NAME}: {ast.unparse(modified_function_assignment)}
else: {ast.unparse(function_assignment)}"""

    branch_call = ast.parse(branch_call_text)

    items[items.index(assignment)] = branch_call

    new_insertion.keys.append(["function","content"])
    new_insertion.values.append([func_name, OPTIONAL_OUTPUT_NAME])




def insert_meta(items, assignment):


    if len(assignment.targets) != 1:
        # assuming it's not something like "a=b=3"
        return

    assignment_text = ast.unparse(assignment)

    variables = extract_variables(assignment_text)

    empty_dict_tree = ast.parse("{}").body[0].value # eww

    values_dict = empty_dict_tree

    for variable in variables:
        values_dict.keys.append(ast.parse(f'"{variable}"').body[0].value)
        values_dict.values.append(ast.parse(f'{variable}').body[0].value)

    # @Ugly
    new_insertion_text = '{"source_code": "'+assignment_text+'","values": '+ast.unparse(values_dict)+'}'
    new_insertion = ast.parse(new_insertion_text).body[0].value

    insert_index = items.index(assignment)+1


    if isinstance(assignment.value, ast.Call):
        # this is assuming it's not inside an expression
        # don't even get an error for that ):
        modify_function_call(items, assignment, new_insertion)



    new_append_text = f'{INSERTIONS_NAME}.append({new_insertion_text})'

    items.insert(insert_index, ast.parse(new_append_text)) # need to insert after







def modify_returns(function_tree):

    def step_down_tree(tree):
        
        
        for item in tree.body:

            if isinstance(item, ast.FunctionDef):
                continue # ignoring nested returns
            

            
            if isinstance(item, ast.Return):

                return_name = item.value.id

                new_return = \
f"""
if {INSERTION_FUNCTIONS_VAR_NAME} is None : return {return_name}
else:  return [{return_name}, {INSERTIONS_NAME}]
"""
                item_index = tree.body.index(item)

                tree.body[item_index] = ast.parse(new_return)
            if "body" in item.__dict__:
                step_down_tree(item)
                
    
    step_down_tree(function_tree)



def insert_code(file, function_names):

    with open(file) as f:
        code = f.read()

    tree = ast.parse(code)
    functions = get_top_functions(tree)

    for function in functions:

        # TODO this needs to be done recursively
            # but only in the case of things i'm handling (just for loops)

        if function.name not in function_names:
            continue


        items = copy.copy(function.body)

        for item in items:
            if isinstance(item, ast.Assign):
                insert_meta(function.body, item)

        start_line_text = f'{INSERTIONS_NAME} = []'
        
        function.body.insert(0, ast.parse(start_line_text).body[0])

        new_arg = ast.arg()
        new_arg.arg = INSERTION_FUNCTIONS_VAR_NAME
        none_tree = ast.parse("None").body[0].value


        function.args.args.append(new_arg)
        function.args.defaults.append(none_tree)

        modify_returns(function)

        

    new_code = ast.unparse(tree)

    new_file_name = ".".join(file.split(".")[0:-1])+"_MODIFIED.py"

    with open(new_file_name,"w") as f:
        f.write(new_code)

    #exec(new_code)
    
    # so, the ONLY thing i care about is stuff in functions
    

function_locations = {}


for function in functions_to_insert:

    module = inspect.getmodule(function)

    file_name = module.__file__
    function_name = function.__name__.split(".")[-1]

    if file_name not in function_locations.keys():
        function_locations[file_name] = []

    function_locations[file_name].append(function_name)



for file_name in function_locations:
    function_names = function_locations[file_name]
    insert_code(file_name, function_names)


pass