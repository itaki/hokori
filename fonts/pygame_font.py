import pygame

default_font = pygame.font.get_default_font()
print(f"default font is {default_font}")

fonts = pygame.font.get_fonts()
print(f"All the fonts")
for font in fonts:
    print (font)