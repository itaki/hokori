
def keyboard_manager(key):
    '''see which tool the keyboard has modified'''
    for tool in tm.tools:
        current_tool = tm.tools[tool]
        if key == current_tool.keyboard_key:
            print(f'Tool {current_tool.name} selected via Keyboard')
            if current_tool.status == 'on':  # Tool is running so turn it off
                current_tool.spindown()
                return
            else:
                current_tool.turn_on()
                return
    else:
        print(f'key {key} not a tool')