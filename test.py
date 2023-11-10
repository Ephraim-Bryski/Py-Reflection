import inspect
for idx,stack in enumerate(inspect.stack()):
    if "exec" in str(stack):
    
        print(idx)