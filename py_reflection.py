
import inspect
import ast
import copy
import shutil
import re
import os
import subprocess
import json
from latex import latexify


META_OUTPUT_NAME = "__META_OUTPUT__"
INSERTIONS_NAME = "__INSERTIONS__"
INSERTION_FUNCTIONS_VAR_NAME = "__INSERTION_FUNCTIONS__"
END_RESULT_VAR = "__END_RESULT__"

LOOP_VAR_NAME = "__LOOP_ASSIGN__"




def _get_top_functions(tree: ast.Module):
    
    """
    gets functions in code
    ignores functions in blocks (e.g. branches, loops)
    """

    def is_function(subtree):
        return isinstance(subtree, ast.FunctionDef)
    
    functions = filter(is_function, tree.body)

    return list(functions)

def _extract_variables(equation: str):

    """
    gets all the variables in a line of code
    """

    # hack i added so that functions won't be included as variables (things with periods won't count and parentheses)
    DUMMY = "DUMMY"
    PERIOD_DUMMY = f"__{DUMMY}__"
    PARENTHESES_DUMMY = PERIOD_DUMMY+" " # extra space so a(b) preserves b
    equation = equation.replace(".",PERIOD_DUMMY).replace("(",PARENTHESES_DUMMY)
    
    # chatgpt code, i hate regexes
    # Regular expression pattern to match variables (assuming variable names contain letters and/or numbers)
    pattern = r'[a-zA-Z_][a-zA-Z0-9_]*'
    variables = re.findall(pattern, equation)
    variables = filter(lambda x: (DUMMY not in x), variables)
    return list(set(variables))

def _modify_function_call(items: list, function_assignment: ast.Assign):
    
    """
    modifies the assignment of a function call with the additional meta output 
    """

    def copy_tree(tree): return ast.parse(ast.unparse(tree)).body[0]

    modified_function_assignment = copy_tree(function_assignment)
    
    output = ast.unparse(modified_function_assignment.targets[0]) # first element gets "a" for "a=b=func()" (nothing to do with multiple outputs)

    modified_output = f'[{output}, {META_OUTPUT_NAME}]'

    modified_function_assignment.targets[0] = ast.parse(modified_output).body[0].value

    modified_function_call = modified_function_assignment.value
    
    keyword_text = f"dummy({INSERTION_FUNCTIONS_VAR_NAME}={INSERTION_FUNCTIONS_VAR_NAME})"
    new_keyword = ast.parse(keyword_text).body[0].value.keywords[0]

    modified_function_call.keywords.append(new_keyword)

    func_name = ast.unparse(modified_function_call.func)


    new_insertion_text = '{"function": "'+func_name+'","content": '+META_OUTPUT_NAME+'}'


    new_append_text = f'{INSERTIONS_NAME}.append({new_insertion_text})'

    branch_call_text = \
f"""if {INSERTION_FUNCTIONS_VAR_NAME} is not None and {func_name} in {INSERTION_FUNCTIONS_VAR_NAME}:
    {ast.unparse(modified_function_assignment)}
    {new_append_text}
else: {ast.unparse(function_assignment)}"""

    branch_call = ast.parse(branch_call_text)

    call_idx = items.index(function_assignment)

    items[call_idx] = branch_call
 

def _modify_assignment(items, assignment, append_parent = INSERTIONS_NAME):


    if len(assignment.targets) != 1:
        # assuming it's not something like "a=b=3"
        return

    assignment_text = ast.unparse(assignment)

    variables = _extract_variables(assignment_text)

    empty_dict_tree = ast.parse("{}").body[0].value # eww

    values_dict = empty_dict_tree

    for variable in variables:
        values_dict.keys.append(ast.parse(f'"{variable}"').body[0].value)
        values_dict.values.append(ast.parse(f'str({variable})').body[0].value)

    new_insertion_text = '{"source_code": "'+assignment_text+'","values": '+ast.unparse(values_dict)+'}'

    insert_index = items.index(assignment)+1


    if isinstance(assignment.value, ast.Call):
        # this is assuming it's not inside an expression
        # don't even get an error for that ):
        _modify_function_call(items, assignment)



    new_append_text = f'{append_parent}.append({new_insertion_text})'

    items.insert(insert_index, ast.parse(new_append_text)) # need to insert after



def _modify_for_loop(parent_items, loop):
    
    iterator = ast.unparse(loop.target)

    initialize_line = f"{LOOP_VAR_NAME} = []"

    loop_dict = f"dict(\
        iterator = '{iterator}', \
        values = list({ast.unparse(loop.iter)}), \
        items = {LOOP_VAR_NAME}\
    )"

    append_line = f"{INSERTIONS_NAME}.append({loop_dict})"

    loop_items = loop.body

    for item in loop_items:
        if isinstance(item, ast.Assign):
            _modify_assignment(loop_items, item, "boop")

    # TODO DON'T CALL BOOP!!!!!!!!!!!!!!
    loop_items.insert(0, ast.parse(f"{LOOP_VAR_NAME}.append(boop)"))
    loop_items.insert(0, ast.parse(f"boop = []"))


    insert_idx = parent_items.index(loop)

    parent_items.insert(insert_idx, ast.parse(append_line).body[0])
    parent_items.insert(insert_idx, ast.parse(initialize_line).body[0])




def _modify_returns(function_tree):

    def step_down_tree(tree):
        
        
        for item in tree.body:

            if isinstance(item, ast.FunctionDef):
                continue # ignoring nested returns
            

            
            if isinstance(item, ast.Return):

                return_content = ast.unparse(item.value)

                new_return = \
f"""
if {INSERTION_FUNCTIONS_VAR_NAME} is None : return {return_content}
else:  return [{return_content}, {INSERTIONS_NAME}]
"""
                
                item_index = tree.body.index(item)

                tree.body[item_index] = ast.parse(new_return)
            if "body" in item.__dict__:
                step_down_tree(item)
                
    
    step_down_tree(function_tree)

def _modify_file(file_name, function_names):

    with open(file_name) as f:
        code = f.read()

    tree = ast.parse(code)

    
    functions = _get_top_functions(tree)

    for function in functions:

        # TODO this needs to be done recursively
            # but only in the case of things i'm handling (just for loops)

        # right now it can only handle an assignment in a loop in a function, but no more depth than that

        if function.name not in function_names:
            continue


        items = copy.copy(function.body)

        for item in items:
            if isinstance(item, ast.Assign):
                _modify_assignment(function.body, item)
            elif isinstance(item, ast.For):
                _modify_for_loop(function.body, item)

        insertions_keyword_text = f"def dummy({INSERTION_FUNCTIONS_VAR_NAME}=None):pass"

        insertions_keyword_tree = ast.parse(insertions_keyword_text).body[0].args

        insertions_arg = insertions_keyword_tree.args[0]
        insertions_default = insertions_keyword_tree.defaults[0]

        function.args.args.append(insertions_arg)
        function.args.defaults.append(insertions_default)




        start_line_text = f'{INSERTIONS_NAME} = []'
        
        function.body.insert(0, ast.parse(start_line_text).body[0])



        _modify_returns(function)

        

    new_code = ast.unparse(tree)


    # doing it this way so i don't have to change the imports
        # giving the new code the same name as the original code
        # i save the original code in a new file and then bring it back in the end after execution
        # seems a bit dangerous but it's finnneeeeeeee



    with open(file_name,"w") as f:
        f.write(new_code)

    #exec(new_code)
    
    # so, the ONLY thing i care about is stuff in functions
    
def _copy_top_level_module(file_path, destination):

    # TODO could be an issue if multiple files share the same module

    path_parts = file_path.replace("\\","/").split("/")

    for i in range(len(path_parts)):

        dir = "/".join(path_parts[0:i+1])

        if dir == "C:":
            # TODO temporary fix cause "C:" gives the current directory files
            # (no idea why)
            continue

        if dir[-3:] == ".py":
            continue # TODO feels a bit hacky

        files = os.listdir(dir)

        if "__init__.py" in files:


            module_name = path_parts[i]

            old_path = "/".join(path_parts[i:])

            new_file_path =  f'{destination}/{old_path}'
            
            module_destination = f'{destination}/{module_name}'

            shutil.copytree(dir, module_destination, dirs_exist_ok=True)
            

            return [new_file_path, module_name]

        
    shutil.copy(file_path, destination)


    file_name = path_parts[-1] # just the name of the file


    new_path = f'{destination}/{file_name}'

    module_name = file_name.replace(".py","")

    return [new_path, module_name]

def insert_meta(functions_to_insert, top_function):

    assert top_function in functions_to_insert, "one of the functions to insert must be the top function"

    function_locations = {}

    for function in functions_to_insert:

        module = inspect.getmodule(function)

        file_path = module.__file__

        if file_path not in function_locations.keys():
            function_locations[file_path] = []

        function_locations[file_path].append(function.__name__)

    

    top_function_path = inspect.getmodule(top_function).__file__

    modified_code_dir = "Modified Code"

    os.makedirs(modified_code_dir,exist_ok=True)

    # makes sure modified code calls this new function instead
    current_file_name = __file__.split("\\")[-1]
    current_function_name = inspect.stack()[0][3]
    with open(f"{modified_code_dir}/{current_file_name}","w") as f:
        f.write(f"def {current_function_name}(dummy1,dummy2): return None")


    module_functions = {}


    for original_file_path in function_locations.keys():

        file_functions = function_locations[original_file_path]

        [new_file_path, module_name] = _copy_top_level_module(original_file_path, modified_code_dir)

        if original_file_path == top_function_path:
            top_module_name = module_name
            new_top_path = new_file_path

        if module_name not in module_functions.keys():
            module_functions[module_name] = []

        for function in file_functions:
            module_functions[module_name].append(function)

        _modify_file(new_file_path, file_functions)


    assert top_function_path is not None, "SHOULD NEVER HAPPEN the top function has to be in a file where the other functions are"


    function_reference_texts = []

    import_lines = []

    for module_name in module_functions.keys():

        inserted_module_name = f"{module_name}_INSERTED__"

        # importing itself leads to circular reference
        is_top_module = module_name == top_module_name

        import_line = f"import {module_name} as {inserted_module_name}"

        if not is_top_module:
            import_lines.append(import_line)

        function_names = module_functions[module_name]


        for function_name in function_names:
        
            if is_top_module:
                reference_text = function_name
            else:
                reference_text = f"{inserted_module_name}.{function_name}"

            function_reference_texts.append(reference_text)


    function_refences_line = f'{INSERTION_FUNCTIONS_VAR_NAME} = [{",".join(function_reference_texts)}]'


    import_text = "\n"+"\n".join(import_lines)+"\n"


    with open(new_top_path, "r") as f:
        top_file_code = f.read()


    top_file_code += import_text

    get_result_line = f"\n{END_RESULT_VAR} = {top_function.__name__}({function_refences_line})[-1]"

    result_file = f"{modified_code_dir}/__END_RESULT__.json"

    write_result_line = \
f"""
import json
with open("{result_file}","w") as f:
    f.write(json.dumps({END_RESULT_VAR},indent = 4))
"""


    add_outer_to_path_line = \
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
"""

    top_file_code = add_outer_to_path_line + top_file_code
    top_file_code += get_result_line
    top_file_code += write_result_line




    #new_top_file_path = f"{modified_code_dir}/top_script.py"

    with open(new_top_path,"w") as f:
        f.write(top_file_code)

    subprocess.call(["python", new_top_path])


    with open(result_file) as f:
        end_result = json.load(f)




    return end_result



