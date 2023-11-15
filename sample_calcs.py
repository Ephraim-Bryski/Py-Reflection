import py_reflection
import importlib
import sample_module
import my_module
import pint
import docx
import create_with_meta

u = pint.UnitRegistry()

importlib.reload(py_reflection)

get_meta = True




def use_output(result):

    if result is None:
        return
    
    doc = docx.Document()

    for item in result:

        is_loop = list(item.keys()) == ["iterator","values","items"]



        if is_loop:

            iterator = item["iterator"]
            iteration_values = item["values"]

            for idx, iteration in enumerate(item["items"]):\
            
                iteration_value = iteration_values[idx]

                iteration_header = f"When {iterator}={iteration_value}:"

                create_with_meta.add_line_to_word(doc, iteration_header, False)

                for line_meta in iteration:
                    latex_line = create_with_meta.construct_line(line_meta)

                    create_with_meta.add_line_to_word(doc, latex_line, True)
        else:
            latex_line = create_with_meta.construct_line(item)
            create_with_meta.add_line_to_word(doc, latex_line, True)


    doc.save("test.docx")



if get_meta:
    result = py_reflection.insert_meta([my_module.A_func], my_module.A_func)
    use_output(result)
else:
    some_result = my_module.A_func()
# this will then 
pass