import pygame
from pygame.locals import *
import time

# Define constants
FONT_NAME = 'meslolgsnf'
LIGHT_GREEN = (144, 238, 144)
LIGHT_GREEN_HOVER = (124, 218, 124)
ORANGE = (255, 165, 0)
ORANGE_HOVER = (235, 145, 0)
ERROR_COLOR = (255, 63, 79)
ERROR_COLOR_HOVER = (255, 64, 80)

ON_COLOR = (129, 249, 0)
ON_COLOR_HOVER = (130, 241, 2)
OFF_COLOR = (25, 209, 229)
OFF_COLOR_HOVER = (41, 225, 230)
SPINDOWN_COLOR = (255, 151, 0)
SPINDOWN_COLOR_HOVER = (255, 152, 1)

TEXT_COLOR = (22, 23, 29)
BACKGROUND_COLOR = (22, 23, 29)
BUTTON_RADIUS = 7
FONT_SIZE_TOOL = 14
FONT_SIZE_GATE = 16


class PG_GUI:

    '''intitalizes pygame canvas'''
    num_of_buttons = len(tm.tools)
    num_of_gates = len(gm.gates)
    pygame.init()
    screen_width = 720
    screen_height = 500
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('R.U.D.I the ShopBot')

    gates_width = 60
    terminal_height = 40
    num_of_tool_buttons_x = 3
    button_panel_width = screen_width-gates_width
    button_width = ((screen_width-gates_width)/num_of_tool_buttons_x)
    button_height = (screen_height-terminal_height) / \
                     (num_of_buttons/num_of_tool_buttons_x)
    gate_width = gate_height = (screen_height-terminal_height)/num_of_gates

    bg = '#16171d'
    clicked = False

class ButtonBase:
    def __init__(self, x, y, name, width, height, screen):
        self.x = x
        self.y = y
        self.name = name
        self.width = width
        self.height = height
        self.screen = screen
        self.button_rect = pygame.Rect(x, y, width, height)
        self.font_size = FONT_SIZE_TOOL if 'Tool' in self.__class__.__name__ else FONT_SIZE_GATE
        self.font = pygame.font.SysFont(FONT_NAME, self.font_size, bold=True)

    def draw_text(self, text, y_offset):
        text_img = self.font.render(text, True, TEXT_COLOR)
        text_len = text_img.get_width()
        self.screen.blit(text_img, (self.x + int(self.width / 2) - int(text_len / 2), self.y + y_offset))

class ToolButton(ButtonBase):
    def draw(self, tool, hover):
        if tool.status == 'on':
            color = ON_COLOR_HOVER if hover else ON_COLOR
        elif tool.status == 'off':
            color = OFF_COLOR_HOVER if hover else OFF_COLOR
        elif tool.status == 'spindown':
            color = SPINDOWN_COLOR_HOVER if hover else SPINDOWN_COLOR
        pygame.draw.rect(self.screen, color, self.button_rect, border_radius=BUTTON_RADIUS)
        self.draw_text(self.name, 5)
        if tool.status == 'spindown':
            info = str(round(tool.spin_down_time - (time.time() - tool.last_used), 1))
        elif tool.status == 'on':
            info = 'on'
        else:
            info = 'off'
        self.draw_text(info, self.font_size + 10)

class GateButton(ButtonBase):
    def draw(self, status, hover):
        if status == 'open':
            color = ORANGE_HOVER if hover else ORANGE
        elif status == 'closed':
            color = LIGHT_GREEN_HOVER if hover else LIGHT_GREEN
        else:
            color = ERROR_COLOR_HOVER if hover else ERROR_COLOR
        pygame.draw.rect(self.screen, color, self.button_rect, border_radius=BUTTON_RADIUS)
        self.draw_text(self.name, (self.height - self.font_size) // 2)

def create_buttons(tm, gm, screen):
    num_of_tool_buttons_x = 3
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    gates_width = 60
    terminal_height = 40
    button_panel_width = screen_width - gates_width
    button_width = (screen_width - gates_width) // num_of_tool_buttons_x
    button_height = (screen_height - terminal_height) // (len(tm.tools) // num_of_tool_buttons_x)
    gate_width = gate_height = (screen_height - terminal_height) // len(gm.gates)

    gui_buttons = {
        tool.name: ToolButton(
            x=(index % num_of_tool_buttons_x) * button_width,
            y=(index // num_of_tool_buttons_x) * button_height,
            name=tool.name,
            width=button_width,
            height=button_height,
            screen=screen
        )
        for index, tool in enumerate(tm.tools.values())
    }

    gate_buttons = {
        gate.name: GateButton(
            x=(index % num_of_tool_buttons_x) * gate_width + (screen_width - gates_width),
            y=(index // num_of_tool_buttons_x) * gate_height,
            name=gate.name,
            width=gate_width,
            height=gate_height,
            screen=screen
        )
        for index, gate in enumerate(gm.gates.values())
    }

    return gui_buttons, gate_buttons

def init_pygame(tm, gm):
    pygame.init()
    screen_width = 720
    screen_height = 500
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('R.U.D.I the ShopBot')
    gui_buttons, gate_buttons = create_buttons(tm, gm, screen)
    return screen, gui_buttons, gate_buttons

def draw_gui(screen, gui_buttons, gate_buttons, gm, tm):
    screen.fill(BACKGROUND_COLOR)
    for button in gui_buttons.values():
        hover = button.button_rect.collidepoint(pygame.mouse.get_pos())
        button.draw(tm.tools[button.name], hover)
    for gate_button in gate_buttons.values():
        hover = gate_button.button_rect.collidepoint(pygame.mouse.get_pos())
        gate_button.draw(gm.gates[gate_button.name].status, hover)
    pygame.display.update()

def handle_events(gui_buttons, gate_buttons, tm, gm):
    run = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            pass  # keyboard_manager(event.key) can be handled if needed
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for button in gui_buttons.values():
                if button.button_rect.collidepoint(event.pos):
                    selected_tool = tm.tools[button.name]
                    if selected_tool.status == 'on':
                        selected_tool.override = False
                        selected_tool.spindown()
                    else:
                        selected_tool.override = True
                        selected_tool.turn_on()
            for gate_button in gate_buttons.values():
                if gate_button.button_rect.collidepoint(event.pos):
                    pass  # Handle gate button click if needed
    return run


class Button_PG_gate():
    padding = 4
    radius = 7
    off_col = '#19d1e5'
    off_col_h = '#29e1e6'
    on_col = '#81f900'
    on_col_h = '#82f102'
    error_col = '#ff3f4f'
    error_col_h = '#ff4050'
    text_col = '#16171d'
    width = gate_width
    height = gate_height
    font_size = 16
    font = pygame.font.SysFont('meslolgsnf', font_size, bold=True)

    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name
        self.button_rect = Rect(self.x+self.padding, self.y+self.padding,
                                self.width-(self.padding*2), self.height-(self.padding*2))

    def open(self):
        pygame.draw.rect(screen, self.on_col, self.button_rect,
                         border_radius=self.radius)

    def open_h(self):
        pygame.draw.rect(screen, self.on_col_h,
                         self.button_rect, border_radius=self.radius)

    def closed(self):
        pygame.draw.rect(screen, self.off_col, self.button_rect,
                         border_radius=self.radius)

    def closed_h(self):
        pygame.draw.rect(screen, self.off_col_h,
                         self.button_rect, border_radius=self.radius)

    def error(self):
        pygame.draw.rect(screen, self.error_col, self.button_rect,
                         border_radius=self.radius)

    def error_h(self):
        pygame.draw.rect(screen, self.error_col_h,
                         self.button_rect, border_radius=self.radius)

    def draw_button(self):
        global clicked
        action = False
        selected_gate = gm.gates[self.name] #select the gate associated with the button

        # get mouse position
        pos = pygame.mouse.get_pos()

        # create pygame Rect object for the button

        # check mouseover and clicked conditions
        if self.button_rect.collidepoint(pos):  # mouse if over the button
            # mouse is pressed but not released
            if pygame.mouse.get_pressed()[0] == 1:
                clicked = True
                if selected_gate.status == 1:
                    self.closed_h()
                elif selected_gate.status == 0:
                    self.open_h()
                elif selected_gate.status == -1:
                    self.error_h()
            # mouse was just released
            elif pygame.mouse.get_pressed()[0] == 0 and clicked == True:
                if selected_gate.status == 1:
                    # open the info window HERE
                    info_window.status = True 
                    info_window.gate = self
                    pass

                clicked = False
                action = True
            else:  # mouse is just over without click
                if selected_gate.status == 1:
                    self.open_h()
                elif selected_gate.status == 0:
                    self.closed_h()
                elif selected_gate.status == -1:
                    self.error_h()

        else:  # mouse is not over button
            if selected_gate.status == 1:
                self.closed()
            elif selected_gate.status == 0:
                self.open()
            elif selected_gate.status == -1:
                self.error()

        # add text to button
        text_img = self.font.render(self.name, True, self.text_col)
        text_len = text_img.get_width()

        screen.blit(text_img, (self.x + int(self.width / 2) -
                    int(text_len / 2), self.y + ((self.font_size/2) + 2)))


        return action





class Error(): # also know as Uniblab
    def __init__(self, name, time_stamp, error):
        self.object =  name
        self.time_stamp = time_stamp
        self.error = error


def create_tool_gui_buttons():
    x = 0
    y = 0
    gui_buttons = {}
    for tool in tm.tools:
        current_tool = tm.tools[tool]
        gui_buttons[current_tool.name] = Button_PG_tool(x,y,current_tool.name)
        x = x + button_width
        if x >= button_panel_width:
            x = 0
            y = y + button_height

    return gui_buttons


def create_gate_gui_buttons():
    x = 0 + (screen_width - gates_width) + (gates_width/2)-(gate_width/2)
    y = 0
    gate_buttons = {}
    for gate in gm.gates:
        gate_buttons[gate] = Button_PG_gate(x,y,gate)
        x = x + gate_width
        if x >= button_panel_width:
            x = 0 + (screen_width - gates_width) + (gates_width/2)-(gate_width/2)
            y = y + gate_height

    return gate_buttons

'''this runs pygame and draws all the buttons on every cycle'''
            screen.fill(bg)
            for button in gui_buttons:
                if gui_buttons[button].draw_button():
                    pass
            for gate in gate_buttons: 
                if gate_buttons[gate].draw_button():
                    pass
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    keyboard_manager(event.key)
                elif event.type == pygame.QUIT:
                    run = False        
            pygame.display.update()