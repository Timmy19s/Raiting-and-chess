from settings import *

pygame.init()

#   //функции
# кнопки
def get_button(): # отловить только нажатие кнопки
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            return pygame.key.name(event.key)

def get_but_mouse(): # отловить нажатие кнопки или мыши
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN: # кнопка
            return pygame.key.name(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN: # мышка нажата
            return f'DOWN{event.button}'
        elif event.type == pygame.MOUSEBUTTONUP: # мышка отпущена
            return f'UP{event.button}'
    

def get_key_mode(): # получить мод
    return pygame.key.get_mods()

def set_cycle(but = 'escape'):
    while 1:
        button = get_button()
        if button == but:
            break

# изображения
def load_img(path,name): # загрузить изображение
    img = pygame.image.load(f'img/{path}/{name}.png')
    
    
    img.set_colorkey(Color.UNVISIBLE)
    
    return img

def draw_img(path,name,blank,C=(0,0)): # нарисовать на холсте
    img = load_img(path, name)
    blank.blit(img,C)

def get_unvis_surf(size : tuple):
    '''
    size - (W,H)
    '''
    surf = pygame.Surface(size)
    surf.fill(Color.UNVISIBLE)
    surf.set_colorkey(Color.UNVISIBLE)
    
    return surf

def blit_surf(blank,img,C=(0,0)):
    '''
    C - rect
    '''
    blank.blit(img,C)




#   //классы
class Run():
    run = True
    
    def stop():
        Run.run = False
        
    def update():
        Run.run = True
        
class Font():
    font = pygame.font.SysFont('calibri',60)
    
    def get_surf_Text(text):
        return Font.font.render(text,True,(0,0,0))
    
    def set_font(font_arg,size):
        Font.font = pygame.font.SysFont(font_arg,size)
    
    def set_size(size):
        Font.font.set_size(size)

class Player(pygame.sprite.Sprite):
    players = pygame.sprite.Group()
    tool = 1
    
    __slots__ = ('image','rect','energy')
    def __init__(self,name,point = 0):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_img('caracters/128',name)
        
        # Энергия
        self.energy = point
        
        # добавим в группу игроков
        self.add(Player.players)
        
        # добавляю в список used_players этого персонажа
        with open(f'{Path.cwd()}/data/save/used_players.txt','a') as file:
            file.write(f'{name}\n')
        # добавляю в список save
        with open(f'{Path.cwd()}/data/save/points.txt','a') as file:
            file.write(f'{point}\n')
    
    def give_energy(button): # дать энергию
        caracter = Player.players.sprites()[int(button)-1]
        
        
        if caracter.energy + Player.tool in range(0,6):
            # дать балл и передвинуть
            caracter.energy += Player.tool
            caracter.rect.y -= Player.tool * 64
            
            # сохранить изменения
            with open(f'{Path_dir}\data\save\points.txt','w') as write:
                for j in Player.players.sprites():
                    write.write(str(j.energy)+'\n')
                    
            # отрисовать персов
            Player.draw_caracters()
            

    def arrange():
        r = 1280//len(Player.players.sprites())
        
        # загружаю машу, чтобы с нее срисовать Rect
        masha = pygame.Surface((128,128))
        n = 0
        l = 9-len(Player.players)
        for i in Player.players.sprites():
            i.rect = masha.get_rect(centerx = r//2 + r*n + random.randint(-10*l,10*l))
            i.rect.y = 592 - i.energy * 64

            n += 1
        
    def draw_caracters():
        # обновить дисплэй
        draw_img('service','background',sc)
        
        # рисую лестницы
        ladder = load_img('rating','ladder')
        for i in Player.players:
            sc.blit(ladder,(i.rect.x,270))
        
        # рисую персонажей
        Player.players.draw(sc)
        
        # рисую сундуки
        chest = load_img('rating','chest')
        for i in Player.players:
            if i.energy == 5:
                sc.blit(chest,(i.rect.x+64,i.rect.y-60))
        
        pygame.display.flip()

    
    
