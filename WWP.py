from defs import *
from os import listdir
# Work With Players

def set_caracters(nums):
    # какие персы есть
    # список используемых персонажей
    with open(f'{Path.cwd()}/data/save/used_players.txt') as used:
        players = [i[:-1] for i in used]
        
    
    
    with open(f'{Path.cwd()}/data/save/list_caracters.txt') as file:
        list_C = [i[:-1] for i in file] # список всех персонажей
        if len(list_C) < nums:
            list_C = [] 
            for i in listdir('img/caracters/512'):
                for j in listdir(f'img/caracters/512/{i}'):
                    if f'{i}/{j[:-4]}' not in players:
                        list_C.append(f'{i}/{j[:-4]}')

    # выбрать случайных персонажей
    new_caracters = []
    for i in range(nums):
        caracter = random.choice(list_C)
        list_C.pop(list_C.index(caracter))
        new_caracters.append(caracter)
        
        
        Player(caracter)
    
    # сохраняю новый список персонажей
    with open(f'{Path.cwd()}/data/save/list_caracters.txt','w') as file:
        for i in list_C:
            file.write(f'{i}\n')
    # указываю доступные кнопки для наград
    Player.pl_keys = tuple([str(i+1) for i in range(len(Player.players.sprites()))])
        
    
    # показ игроков
    if HTS[1] == 1:
        sc.fill(Color.BACKGROUND_blue)
        for i in new_caracters:
            draw_img('caracters/512',i,sc,(384,104))
            pygame.display.flip()
            
            set_cycle('space')
    
    # перераспределить персонажей
    Player.arrange()
            
def set_new_Pl(): # сколько игроков
    
    def draw_num(): # рисую колл игроков
        surf = load_img('WWP', 'num_pl')
        rect = surf.get_rect(center = (640,360))
        
        # номер
        text = 'save' if len_pl == 9 else str(len_pl)
        text = Font.get_surf_Text(text)
        rectT = text.get_rect(center = (128,64))
        surf.blit(text,rectT)
        
        sc.blit(surf,rect)
        pygame.display.flip()

    def work_with_save(load):
        '''
        load - True/False\n
        загрузить или стереть
        '''
        players = []
        if load:
            # загрузить список баллов
            points = []
            with open(f'{Path.cwd()}/data/save/points.txt') as file:
                for i in file:
                    points.append(int(i[:-1]))
            
            # загрузить список персонажей
            with open(f'{Path.cwd()}/data/save/used_players.txt') as file:
                for i in file:
                    players.append(i[:-1])
                    
            
                    
        # обновить список персонажей
        with open(f'{Path.cwd()}/data/save/used_players.txt','w') as file:
            file.write('')
        
        # обновить список баллов
        with open(f'{Path.cwd()}/data/save/points.txt','w') as file:
            file.write('')
        
        # загрузка персов
        for i in range(len(players)):
            Player(players[i],points[i])
            
        if load:
            # указываю доступные кнопки для наград
            Player.pl_keys = tuple([str(i+1) for i in range(len(Player.players.sprites()))])
    
    # //колличество игроков
    sc.fill(Color.BACKGROUND_blue)
    pygame.display.flip()

    
    if HTS[2] == 0:
        len_pl = 1
        draw_num()
        while Run.run:
            but = get_button()

            if but == 'return': # выбрать
                Run.stop()
            
            elif but == 'right': # добавить одного
                if len_pl <9:
                    len_pl += 1
                else:
                    len_pl = 1
                
                draw_num()
                
            elif but == 'left': # убрать одного
                if len_pl > 1:
                    len_pl -= 1
                else:
                    len_pl = 8      
                
                draw_num()
        
        #обновить save
        if len_pl != 9:
            work_with_save(False)
    
            set_caracters(len_pl)
            
        else:
            work_with_save(True)
    
    else:
        work_with_save(False)
        
        set_caracters(HTS[2])

