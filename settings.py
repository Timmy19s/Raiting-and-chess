# импорт
from pathlib import Path
import pygame
import random

pygame.init()

# системные константы
Path_dir = Path.cwd()
SIZE_window = (1280,720)
clock = pygame.time.Clock()
FPS = 30

# цвета
class Color():
    UNVISIBLE = (255,174,201)
    BACKGROUND_blue = (137,217,255)
    WHITE = (255,255,255)
    
# языки
rus_symbols = dict(zip("qwertyuiop[]asdfghjkl;'zxcvbnm,","йцукенгшщзхъфывапролджэячсмитьбю"))


# как начать
if 1:
    with open(f'{Path_dir}/data/How_to_start.txt') as file: # загружаю файл "How_to_start.txt"
        HTS = []
        for i in file:
            HTS.append(int(i[1]))


    if HTS[0] == 0: # кортеж HTS
        HTS = (1,1,0)
    else:
        HTS.pop(0)
        HTS = tuple(HTS)


    if HTS[0] == 0: # создать дисплей 
        sc = pygame.display.set_mode((SIZE_window))
    else:
        sc = pygame.display.set_mode((SIZE_window),pygame.FULLSCREEN)
        
