


class Tool:
    def __init__(self, tool):
        self.tool_dict = tool
        self.pins_used = []
        self.id_num = tool['id_num']
        self.name = tool['name']
        self.status = 'off'
        self.override = False
        self.gate_prefs = tool['gate_prefs']
        if tool['button'] != {}:
            self.create_button(tool['button'])
            self.pins_used.append(tool['button']['pin'])

        if tool['led'] != {}:
            self.create_led(tool['led'])
            if tool['led']['type'] == 'PWMLED':
                self.pins_used.append(tool['led']['pin'])
            elif tool['led']['type'] == 'RGB':
                self.pins_used.extend(tool['led']['pins'])

        if tool['volt'] != {}:
            self.voltage_sensor = vs.Voltage_Sensor(tool['volt'])
            print(f"Initialized Voltage Sensor for {self.name}")

        self.keyboard_key = tool['keyboard_key']       
        self.spin_down_time = tool['spin_down_time']
        self.last_used = 0
        self.flagged = True

    def create_button(self, btn_dict):
        print(f"Creating {self.name} button at address {btn_dict['address']} on pin {btn_dict['pin']}")
        if btn_dict['address'] == 'pi':  # a button that is directly attached to the pi
            self.btn = Button(btn_dict['pin'])
            self.btn.when_pressed = self.button_cycle
        else:
            print('Buttons not directly connected to pi are not supported right now')

    def create_led(self, led_dict):
        if led_dict['address'] == 'pi':
            if led_dict['type'] == "RGB":
                self.led = RGBLED(led_dict['pins'][0], led_dict['pins'][1], led_dict['pins'][2])
                self.led_type = "RGB"
                print(f"created RGBLED on {led_dict['pins'][0]}, {led_dict['pins'][1]}, {led_dict['pins'][2]}")
            elif led_dict['type'] == "PWMLED":
                self.led = PWMLED(led_dict['pin'], initial_value=0)
                self.led_type = "PWMLED"
                print(f"Creating an {led_dict['type']} LED on {led_dict['address']} on pin {led_dict['pin']}")
            elif led_dict['type'] == "RELAY":
                self.led = OutputDevice(led_dict['pin'], initial_value=False)
                self.led_type = "RELAY"
            else:
                print(f"no led created for {self.name}")
        else:
            print('LEDs not directly connected to pi are not supported right now')

    def button_cycle(self):
        if self.status == 'on':
            self.override = False
            print(f"{self.name} button pressed. Tool and Override OFF")
            self.spindown()
        else:
            self.override = True
            print(f"{self.name} button pressed. Tool and Override engaged")
            self.turn_on()

    def turn_on(self):
        self.status = 'on'
        self.flagged = True
        if hasattr(self, "led"):
            if self.led_type == "RGB":
                self.led.pulse(fade_in_time=1, fade_out_time=1, on_color=(.51, .9, 0), off_color=(.6, 1, .1), n=None, background=True)
            elif self.led_type == "PWMLED":
                self.led.on()
            elif self.led_type == "RELAY":
                self.led.on()
        print(f'----------->{self.name} turned ON')

    def spindown(self):
        self.status = 'spindown'
        self.last_used = time.time()
        if hasattr(self, "led"):
            if self.led_type == "RGB":
                self.led.pulse(fade_in_time=1, fade_out_time=1, on_color=(1, .59, 0), off_color=(0, 0, 0), n=None, background=True)
            elif self.led_type == "PWMLED":
                self.led.pulse(fade_in_time=1, fade_out_time=1, n=None, background=True)
            elif self.led_type == "RELAY":
                pass
        print(f'----------->{self.name} set to SPINDOWN for {self.spin_down_time}')

    def turn_off(self):
        self.status = 'off'
        self.flagged = True
        if hasattr(self, "led"):
            if self.led_type == "RGB":
                self.led.color = (.1, .82, .90)
            elif self.led_type == "PWMLED":
                self.led.value = .1
            elif self.led_type == "RELAY":
                self.led.off()
        print(f'----------->{self.name} turned OFF')