import pygame
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
