from pickle import load,dump
from defs import *
from random import choice, randint, shuffle
from os import listdir
from numpy import array
from time import sleep
from os import listdir


#   константы
with open(f'{Path_dir}/data/chess_mode/rules.txt') as file: # правила движения
    rules = True if file.readline() == 'on' else False
color = None
ex = None

score = ''
path = None

turn = 'W'
mode = 'CallCell'
end = 'defeat'

timers = [300,5]

class Figs():
    # ИИ
    AI = 'robot'
    
    # поле с фигурами
    field_fig = array([array([None for i in range(8)]) for i in range(8)])
    eaten_fig = None
    
    # территории фигур
    territory = array([array([array([0 for i in range(8)]) for i in range(8)]) for i in range(2)])
    
    # армии
    my_troops = []
    animy_troops = []
    
    # переменная для шаха
    check = False
    
    # рокировка
    castling = False
    
    # мышка зажата
    mouse = False
    
    # запись анализа
    rec = False
    
    def __init__(self,name,location):
        '''
        name - Cn (Color name) \n
        location - (x,y)
        '''
        # ранг фигуры
        self.name = name
        
        # положение
        self.x,self.y = location
 
        # добавляю в поле с фигурами
        Figs.field_fig[self.y,self.x] = self
        

        if name[0] == color[0]: # добавляю в войска и определяю клан
            Figs.my_troops.append(self)
            
            self.clan = 'good'
            self.animy = Figs.animy_troops

            # король должен стоять в начале списка
            if name[1] == 'k' and len(Figs.my_troops) > 1:
                Figs.my_troops[0],Figs.my_troops[-1] = Figs.my_troops[-1],Figs.my_troops[0]
            
        else:
            Figs.animy_troops.append(self)
            
            self.clan = 'evil'
            self.animy = Figs.my_troops

            # король должен стоять в начале списка
            if name[1] == 'k' and len(Figs.animy_troops) > 1:
                Figs.animy_troops[0],Figs.animy_troops[-1] = Figs.animy_troops[-1],Figs.animy_troops[0]

        # условия рокировки
        if name[1] == 'k':
            self.castle = [True,True] if Figs.castling else False
            
    def set_aur(self): # создать ауру вокруг короля
        # доступные пути
        av_cells = []
    
        for i in (-1,1):
            # верхние и нижние клетки
            for j in range(-1,2):
                if self.x+j in range(8) and self.y+i in range(8):
                    av_cells.append((self.x+j,self.y+i))
            
            # боковые клетки
            if self.x+i in range(8) and self.y in range(8):
                av_cells.append((self.x+i,self.y))
        
        self.aur = av_cells

    def WhoIsIt(self,x,y): # кто в указанной клетке от данной фигуры
        
        if x in range(8) and y in range(8):
            cell = Figs.field_fig[y,x]
            if cell == None: # если пусто
                res = 'ec'
            
            elif cell.clan == self.clan: # союзник
                res = 'fr'
            
            else: # враг
                res = 'an'
            

            # не захватывает территорию впереди
            if self.name[1] == 'p' and self.x == x:
                pass
            
            else: # территория фракции
                i = 0 if self in Figs.my_troops else 1
                if Figs.territory[i][y,x] < 8:
                    Figs.territory[i][y,x] += 1

                # sym = '+' if self.name[0] == color[0] else '-' # символ своей команды
                
                # if Figs.territory[y,x] == '0': # территория опр фракции
                #     Figs.territory[y,x] = sym
                
                # elif Figs.territory[y,x] != '*' and Figs.territory[y,x] != sym: # спорная территория
                #     Figs.territory[y,x] = '*'
                
                    
                    
            return res
        
    def get_av_cells(self): # доступные ходы + обработка веса
        # координаты
        x,y = self.x, self.y
        
        def avail_pawn(): # пешка
            # доступные пути 
            av_cells = []
            
            # направление
            direct = -1 if self.name[0] == color[0] else 1
            
            # ход команды этой пешки
            if self.name[0] == turn: 
                # поля впереди
                res = self.WhoIsIt(x,y+direct) # кто стоит на этом месте
                if res == 'ec':
                    av_cells.append((x,y+direct))
                    
                    # турборежим
                    st = 6 if self.name[0] == color[0] else 1 # ОТКУДА можно включить турборежим
                    res = self.WhoIsIt(x,y+2*direct) # кто стоит на этом месте
                    if y == st and res == 'ec':
                        av_cells.append((x,y+2*direct))
                        
            
                # поля для атаки
                for i in (-1,1):
                    res = self.WhoIsIt(x+i,y+direct) # кто стоит на этом месте
                    if res == 'an':
                        av_cells.append((x+i,y+direct))
            
            else: # ход не этой команды
                # поля для атаки
                for i in (-1,1):
                    if self.WhoIsIt(x+i,y+direct) != None:
                        av_cells.append((x+i,y+direct))
            
            return av_cells

        def avail_king():
            # создать ауру вокруг себя
            self.set_aur()
            
            # *если ход команды короля
            if turn == self.name[0]:
                # * исключаю из ауры поля, которые находятся под влиянием чужой фракции
                animy_territory = Figs.territory[1] if self in Figs.my_troops else Figs.territory[0]

                av_cells = [] 
                for i in self.aur:
                    x,y = i

                    self.WhoIsIt(x,y) # захватить территорию
            
                    if (Figs.field_fig[y,x] == None or Figs.field_fig[y,x].name[0] != self.name[0]) and animy_territory[y,x] == 0:
                        av_cells.append(i)
                
                
                # * рокировка
                if Figs.castling == True and self.name[0] == turn: # может сделать рокировку и его ход
                    # можно ли рокироваться конкретно этой команде
                    if self.castle != False:
                        # есть ли доступные ладьи
                        for i in (0,1):
                            xi = 7 if i == 1 else 0
                            rock = Figs.field_fig[self.y, xi]
                            
                            # на месте ладьи никого нет или стоит не своя ладья
                            if rock == None or rock.name != f'{self.name[0]}r': 
                                self.castle[i] = False # отменяю рокировку по этой стороне

                        # есть ли припятсвия?
                        if self.castle[0] == True: # левая рокировка
                            able = True
                            for xi in range(self.x-2, self.x+1): # поля под атакой или какая-либо фигура
                                if animy_territory[self.y,xi] != 0 or Figs.field_fig[self.y,xi] not in (None, self):
                                    able = False
                                    break
                                
                            if able:
                                av_cells.append((self.x-2,self.y))
                                
                        if self.castle[1] == True: # правая рокировка
                            able = True
                            for xi in range(self.x,self.x + 3): # поля под атакой или какая-либо фигура
                                if animy_territory[self.y,xi] != 0 or Figs.field_fig[self.y,xi] not in (None, self):
                                    able = False
                                    break
                                
                            if able:
                                av_cells.append((self.x+2,self.y))
                        
                        
                        if self.castle == [False,False]: # отмена рокировки совсем
                            self.castle = False
                        
            else:
                av_cells = list(self.aur)
                
                [self.WhoIsIt(c[0],c[1]) for c in av_cells] # захватить территорию

            return av_cells

        def avail_goniec():
            # доступные пути
            av_cells = []
            
            # перебираю коэф k
            for k in (-1,1):
                # ищу b
                b = y-x*k
                
                # справа на лево
                for rng in (range(x+1,8),reversed(range(0,x))):
                    pirce = False
                    for i in rng:
                        yi = k*i+b # координата по y
                        res = self.WhoIsIt(i,yi) # кто на этом месте
                        
                        if res in ('ec','an'):
                            av_cells.append((i,yi))
                            
                            if res == 'an' and Figs.field_fig[yi,i].name[1] == 'k': # простреливаю короля
                                pirce = True
                            
                            elif res == 'an' or pirce:
                                break
                        
                        elif res == 'fr':
                            break
            
            return av_cells

        def avail_rock():
            # доступные пути
            av_cells = []
            
            # горизонталь
            for rng in (range(x+1,8),reversed(range(0,x))):
                pirce = False # прохожу сквозь короля
                
                for i in rng:
                    res = self.WhoIsIt(i,y) # кто на этом месте
                    
                    if res in ('ec','an'):
                        av_cells.append((i,y))
                        
                        if res == 'an' and Figs.field_fig[y,i].name[1] == 'k': # простреливаю короля
                            pirce = True
                        
                        elif res == 'an' or pirce:
                            break
                        
                            
                        
                    elif res == 'fr':
                        break
            
            # вертикаль
            for rng in (range(y+1,8),reversed(range(0,y))):
                pirce = False # прохожу сквозь короля
                
                for i in rng:
                    res = self.WhoIsIt(x,i) # кто на этом месте
                    
                    if res in ('ec','an'):
                        av_cells.append((x,i))
                        
                        if res == 'an' and Figs.field_fig[i,x].name[1] == 'k': # простреливаю короля
                            pirce = True
                            
                        elif res == 'an' or pirce:
                            break
                        
                    elif res == 'fr':
                            break
            
            return av_cells

        def avail_queen():
            
            # ходы ладьи
            av_cells = avail_rock()
            
            # ходы слона
            av_cells += avail_goniec()
            
            return av_cells

        def avail_horse():
            # доступные пути
            av_cells = []
            
            for i in (-2,2):
                for j in (-1,1):
                    # *горизонтальные ходы
                    xi = x + i
                    yi = y + j
                    res = self.WhoIsIt(xi,yi) # кто стоит на этом месте
                    
                    if res in ('ec','an'):
                        av_cells.append((xi,yi))
                    
                    
                    # *вертикальные
                    xi = x + j
                    yi = y + i
                    res = self.WhoIsIt(xi,yi) # кто стоит на этом месте
                    
                    if res in ('ec','an'):
                        av_cells.append((xi,yi))
            
            return av_cells

        defFigs = {'p' : avail_pawn,
                'k' : avail_king,
                'g' : avail_goniec,
                'r' : avail_rock,
                'q' : avail_queen,
                'h' : avail_horse}

        return defFigs[self.name[1]]()

    def change_turn(wich_turn : str):
        global turn
        
        if wich_turn == 'my_turn':
            turn = Figs.my_troops[0].name[0]
        elif wich_turn == 'animy_turn':
            turn = Figs.animy_troops[0].name[0]
        else:
            raise TypeError('turn не поменялся!')
     
class AI():
    name = 'Robot'
    spend_time = 'robt'
    blitz = False
    num_Check = 0
    
    def set_AI(name):
        names = {'Robot' : 'robt',
                 'Junior' : 'long',
                 'Weasel' : 'norm',
                 'Bully' : 'norm',
                 'Tricky' : 'norm',
                 'Biter' : 'norm',
                 'Smarty' : 'long',
                 'Fierce' : 'norm',
                 'Hardy' : 'norm'}
        
        # изменить имя
        AI.name = name
        
        AI.spend_time = names[name]
    
    def gen_avMoves(fig):
        def lenth_path(pos_f,av_cells,lenth): # длина пути
            lenth **=2
            x0,y0 = pos_f
            
            for cell in list(av_cells):
                x,y = cell
                if (x-x0)**2 > lenth or (y-y0)**2 > lenth:
                    av_cells.pop(av_cells.index(cell))
            
            return av_cells
        
        
        av_cells = []
        
        if AI.name == 'Junior':
            if fig.name[1] in ('k','p'): # ходят только король и пешки если король не остался один
                av_cells = fig.get_av_cells()
        
        elif AI.name == 'Weasel': # король, пешки, кони и слоны на 3 клетки
            if fig.name[1] in ('k','p','h'): 
                av_cells = fig.get_av_cells()
            
            elif fig.name[1] == 'g':
                pos = fig.x, fig.y
                av_cells = lenth_path(pos,fig.get_av_cells(),3)
        
        elif AI.name == 'Bully': # король, пешки, кони и ладьи на 4 клеток
            if fig.name[1] in ('k','p','h'):
                av_cells = fig.get_av_cells()

            elif fig.name[1] == 'r':
                pos = fig.x, fig.y
                av_cells = lenth_path(pos,fig.get_av_cells(),4)
                
        elif AI.name == 'Tricky': # король, пешки, кони и другие на 2-3 клеток
            if fig.name[1] in ('k','p','h'):
                av_cells = fig.get_av_cells()
            
            else:
                k = 2 if fig.name[1] == 'g' else 3
                pos = fig.x, fig.y
                av_cells = lenth_path(pos,fig.get_av_cells(),k)
            
        elif AI.name == 'Biter': # кусала ходит за всех, но может реализовать достаточно хорошо только слонов
            if fig.name[1] in ('k','p','g','h'):
                av_cells = fig.get_av_cells()
            
            else:
                pos = fig.x, fig.y
                av_cells = lenth_path(pos,fig.get_av_cells(),3)
            
            
        elif AI.name == 'Robot':
            av_cells = fig.get_av_cells()
            
        return av_cells 
    
            

    def low_time():
        if AI.blitz == True:
            lt = {'robt' : 'robt',
                'long' : 'norm',
                'norm' : 'fast',
                'fast' : 'robt'}
            
            AI.spend_time = lt[AI.spend_time]
              
    # ход робота
    def genMoves(): # сгенерировать все возможные ходы
        '''
        откуда -> куда
        '''
        global path
        
        # словарь из веса и ходов
        moves = {}
        for i in Figs.animy_troops: # оцениваю каждый доступный ход
            av_cells = AI.gen_avMoves(i)
            
            for j in av_cells:
                path = ((i.x,i.y),j)
                res = imitMove() # сымитировать такой ход и получить оценку
                
                if 'defeat' != res: # ход не ведет к поражению
                    if res in moves:
                        moves[res].append(path)
                    else:
                        moves[res] = [path]
        
        
        # сортировка ходов   
        moves = sorted(moves.items(),reverse = True)
        moves = [i[1] for i in moves]
        
        # *выбрать лучший ход
        best = None
        if len(moves) > 0:            
            # лучший ход
            best = choice(moves[0])
        
        return best

    def spendTime(): # бот думает
        '''
        robt: 1 секунда
        fast: 1-4 секунды
        norm: 2-8 секунд
        long: 3-12 секунд
        '''
        global timers, end
        timer = {'robt' : 1,
                'fast' : randint(1,4),
                'norm' : randint(2,8),
                'long' : randint(3,12)}
        
        time_t = timer[AI.spend_time]*30
        while 1:
            clock.tick(30)
            if time_t < 0:
                break
            else:
                time_t -= 1
                if time_t % 30 == 0: #отрисовать таймер
                    timers[0] -= 1
                    draw_timer()
                    pygame.display.flip()
                    
                    if timers[0] == 0: #время вышло у ИИ
                        draw_message('defeat')
                        Run.run = False
                        end = 'win'
                        break

    def noWay():
        global end
        if Figs.check: # шах и мат
            draw_message('defeat') # поражение ИИ
            end = 'win' # игрок победил
        
        else: # пат
            
            for i in Figs.animy_troops:
                if i.name[1] == 'k':
                    king = i
                    break 
            
            Figs.change_turn('my_turn')
            king.set_aur()
            Figs.change_turn('animy_turn')
            highlighter(king.aur,(255,0,0))
            draw_message('stalemate')
            
            end = 'stalemate' # ничья
            
        Run.run = False

    # сделать ход
    def makeMove():
        global path
        move = AI.genMoves()
        if move != None: # есть пути
            path = move
            
            # пойти
            AI.spendTime()
            if Run.run:
                moveFig()
        else:
            AI.noWay()
    
    
    def set_Debout(debout = 'little_Dragon'):
        # список дебютов
        pass
        
        
        
                  
class Company():
    mes_ind = 0
    
# действия
def set_new_ex(): # открываю новые задачи
    with open(f'{Path_dir}/data/chess_mode/{mode}/{ex}.txt','rb') as file:
        global color,data
        color,data = load(file)
    
    # создаю объект класса
    for xi in range(8):
        for yi in range(8):
            if data[yi,xi] != 'ec':
                obj_f = Figs(data[yi,xi],(xi,yi))
    
    # обновить территорию
    analysis_board()
    
    # кто ходит первый
    if mode == 'Chess&mate_1':
        global turn
        if color == 'Black': 
            turn = 'B' 

def update_data():
    global color, score, path, turn, mode
    color = None

    score = ''
    path = None

    turn = 'W'
    
    # поле с фигурами
    Figs.field_fig = array([array([None for i in range(8)]) for i in range(8)])
    
    # армии
    Figs.my_troops = []
    Figs.animy_troops = []
    
    # переменная для шаха
    Figs.check = False
 
def analysis_board():
    weight = 0
    
    # какая команда начинает первой определять свою территорию?
    first_group = Figs.animy_troops if turn == color[0] else Figs.my_troops # команда, которая сделала ход
    second_group = Figs.my_troops if turn == color[0] else Figs.animy_troops # команда, которая делает ход
    
    # обновить территорию
    Figs.territory = array([array([array([0 for i in range(8)]) for i in range(8)]) for i in range(2)])
    for group in (first_group, second_group):
        for fig in group:
            w = len(fig.get_av_cells())
            
            weight += -1*w if group == first_group else w
    
    
    # обновить веса
    for group in (first_group, second_group):
        animy_territory = Figs.territory[1] if group == Figs.my_troops else Figs.territory[0]
        self_territory = Figs.territory[0] if group == Figs.my_troops else Figs.territory[1]
        for fig in group:
            
            w = 0 
            name = fig.name
            # пешка
            if name[1] == 'p':
                y = 8 - fig.y if fig.name[0] == color[0] else 1 + fig.y 
                w = 10 + (y-2)**2
            
            else:
                price = {'k' : 40,
                     'q' : 90,
                     'g' : 30,
                     'h' : 30,
                     'r' : 50,
                     'p' : 10}

                w = price[name[1]]
            
            
            # фигура под ударом
            if animy_territory[fig.y,fig.x] != 0: # защищенная фигура

                # фигура прикрыта
                if self_territory[fig.y,fig.x] != 0:
                    w *= 0.9

                else:
                    c = 0.3 if fig.name[0] == turn else 0.9 # если ход команды этой фигуры, потеря болезнееней
                    w *= c
            
            weight += -1*w if name[0] == color[0] else w
    
    # шах и мат моему королю
    if turn != color[0]: # ход ИИ
        # мой король
        King = Figs.my_troops[0]

        # допустимые ходы
        av_cells = []
        King.set_aur()
        for i in King.aur:
            x,y = i
            if (Figs.field_fig[y,x] == None or Figs.field_fig[y,x].name[0] != color[0]) and Figs.territory[1][y,x] == 0:
                av_cells.append(i)

        k = 8 - len(av_cells) # коэффициент награды

        # есть ли фигура под ударом
        for cell in King.aur: 
            x,y = cell
            

            # ищу фигуры под ударом
            if Figs.field_fig[y,x] != None and Figs.field_fig[y,x].name[0] != color[0] and Figs.territory[0][y,x] != 0: # фигура ИИ под ударом

                # если 1 атака, но у ИИ фигура не защищена, или больше одной атаки
                if Figs.territory[0][y,x] == 1 and Figs.territory[1][y,x] == 0 or Figs.territory[0][y,x] > 1:
                    k -= price[Figs.field_fig[y,x].name[1]] // 10

        if Figs.territory[1][King.y, King.x] != 0: # поставлен шах
            w = 200 if len(av_cells) == 0 else (10*k - AI.num_Check * 100) # очки за поля
        else:
            w = 5*k
            
            # !нельзя допустить пат
            # no_way = True
            # for i in Figs.my_troops: # оцениваю каждый доступный ход
            #     if i.name[1] != 'k' and len(AI.gen_avMoves(i)) != 0:
            #         no_way = False
            #         break
            
            # if no_way:
            #     w = -500
        
        weight += w

    
    return weight
        
def LetToInd(let): # буква в индекс
    if color == 'White':
        return 'abcdefgh'.find(let)
    else:
        return 'hgfedcba'.find(let)

def NumToInd(num): # цифра в индекс
    return (8-int(num)) if color == 'White' else (int(num)-1)

def set_timer():
    global timers
    
    with open(f'{Path_dir}/data/chess_mode/timer.txt') as file: # реплики
        # время противника
        timers[0] = int(file.readline()[:-1])
        # мое
        timers[1] = int(file.readline()[:-1])



# действия с фигурами
def imitMove(): # имитация хода
    global turn

    # ** подготовка! 
    # координаты
    xNew,yNew = path[1]
    xOld,yOld = path[0]
    
    # фигура
    fig = Figs.field_fig[yOld,xOld]
    
    # поле, куда встанет эта фигура
    Figs.eaten_fig = Figs.field_fig[yNew,xNew]
    
    
    
    
    # ** переставить!
    # удалить фигуру из списка врагов
    if Figs.field_fig[yNew,xNew] != None:
        fig.animy.pop(fig.animy.index(Figs.field_fig[yNew,xNew]))
        
    # передвинуть фигуру
    Figs.field_fig[yOld,xOld] = None
    Figs.field_fig[yNew,xNew] = fig
    
    # новое положение фигуры
    fig.x,fig.y = xNew,yNew
    
    
    
        
    # ** обработка!
    res = None

    # результат такого хода
    check()
    if Figs.check != False: # если все еще шах, то этот ход приведет к поражению
        res = 'defeat'

    else: # любая другая оценка хода
        res = analysis_board()

    
    
    
    # ** возвращаю все на место!
    # передвинуть фигуру
    Figs.field_fig[yOld,xOld] = fig
    Figs.field_fig[yNew,xNew] = Figs.eaten_fig
    
    # возращаю положение фигуры
    fig.x,fig.y = xOld,yOld
    
    # возвращаю съеденную фигуру на место
    if Figs.eaten_fig != None:
        fig.animy.append(Figs.eaten_fig)
    
    
    
    # ** конец
    return res

def moveFig():
    global score,path
    def do(): # исполнить
        global turn
        
        # удаляю фигуру из списка врагов
        if Figs.field_fig[yNew,xNew] != None:
            fig.animy.pop(fig.animy.index(Figs.field_fig[yNew,xNew]))
            
        # сдвинуть фигуру
        Figs.field_fig[yOld,xOld] = None
        Figs.field_fig[yNew,xNew] = fig
        
        # сделана рокировка
        if fig.name[1] == 'k' and (xNew - xOld)%2 == 0 and yNew == yOld:
            # координаты ладьи
            rOld = (0,yOld) if xNew - xOld == -2 else (7,yOld)
            rNew = (xNew + 1,yNew) if xNew - xOld == -2 else (xNew - 1,yNew)
            
            # сдвинуть ладью
            rock = Figs.field_fig[rOld[1],rOld[0]]
            Figs.field_fig[rOld[1],rOld[0]] = None
            Figs.field_fig[rNew[1],rNew[0]] = rock
            
            # новое положение ладьиэ
            rock.x,rock.y = rNew
        
        if fig.name[1] == 'k': # если сходил король, то рокировка больше невозможна
            fig.castle = False
        
        
        # новое положение
        fig.x,fig.y = xNew,yNew
        
        # оказались ли пешка на границе
        if fig.name[1] == 'p' and fig.y in (0,7):
            # передвинуть неповышенную пешку
            update_chess()
            level_up(fig.y)
        
        # ход другого игрока
        turn = 'W' if turn == 'B' else 'B'
        
        # ести ли шах
        check()
        
        # обновить
        update_chess()
        
        # записать ход
        with open(f'{Path.cwd()}/data\chess_mode/bag_files\save_board.txt', 'wb') as file:
            field = []
            for str_i in Figs.field_fig:
                list_st = []
                for i in str_i:
                    if i != None:
                        list_st.append(i.name)
                    else:
                        list_st.append('ec')
                field.append(array(list_st))
            dump((color,array(field)),file)
    
        if Figs.check != False:
            AI.num_Check += 2
        elif turn == color[0]:
            AI.num_Check -= 1 if AI.num_Check > 0 else 0
        

    def level_up(h): # пешка становится фигурой
        global timers
        
        if h == 0: # я восстанавливаю фигуру
            # TODO письмо пешки
            # полотно
            surf = get_unvis_surf((434,228))
            
            # фон фигуры
            col_b = (181,136,99) if turn == 'B' else (240,217,181)
            sur_b = pygame.Surface((85,85))
            sur_b.fill(col_b)
            surf.blit(sur_b,(30,31))
            
            # рисую фигуру
            draw_img('chess',f'{turn}p',surf,(30,31))
                    
            # рисую рамку
            draw_img('chess','level_up',surf)
            
            # рисую полотно
            sc.blit(surf,(80,295))
            pygame.display.flip()
            
            # TODO 2 этап
            sel = None
            but = False
            new_sel = (41,32)
            t = 0
            while but == False:
                clock.tick(30)
                # проверка позиции
                pos = pygame.mouse.get_pos()
                if pos[0] < 329 and pos[1] < 426: # королева
                    new_sel = (41,32)
                elif pos[0] > 329 and pos[1] < 426: # ладья
                    new_sel = (133,32)
                elif pos[0] < 329 and pos[1] > 426: #слон
                    new_sel = (41,82)
                elif pos[0] > 329 and pos[1] > 426: # конь
                    new_sel = (133,82)
                
                # поменять стрелку
                if sel != new_sel:
                    sel = new_sel
                    
                    surf = load_img('chess','level_up_figs')
                    
                    pygame.draw.aaline(surf,(128,128,128),(87,57),sel)
                    sc.blit(surf,(242,369))
                    
                    pygame.display.flip()
                
                for i in pygame.event.get():
                    if i.type == pygame.MOUSEBUTTONDOWN:
                        if i.button == 1:
                            but = True
                
            # меняю фигуру
            figs = {(41,32) : 'q',
                    (133,32) : 'r',
                    (41,82) : 'g',
                    (133,82) : 'h'}
            fig.name = f'{turn}{figs[sel]}'
                
        else: # ИИ
            
            #меняю имя
            fig.name = f'{turn}q'
            
        
    # координаты
    xNew,yNew = path[1]
    xOld,yOld = path[0]
    
    # фигура
    fig = Figs.field_fig[yOld,xOld]
    
    # переставляю фигуру
    if rules: # в соответствии с правилами
        if (xNew,yNew) in fig.get_av_cells():
            Figs.rec = True
            if imitMove() != 'defeat': # Не открывает короля под удар + записывает результат
                do()
                Figs.rec = False
             
    else: # без правил
        do()
    
    # обновить score  
    score = ''
    
    # обновить путь
    path = None

def check():
    first_group  = Figs.animy_troops if turn == color[0] else Figs.my_troops # команда, которая сделала ход
    second_group = Figs.my_troops if turn == color[0] else Figs.animy_troops # команда, которая делает ход

    # обновить территорию
    Figs.territory = array([array([array([0 for i in range(8)]) for i in range(8)]) for i in range(2)])
    for group in (first_group, second_group):
        for fig in group:
            fig.get_av_cells()
    
    
    # территория врага
    animy_territory = Figs.territory[1] if second_group == Figs.my_troops else Figs.territory[0]
    
    # положение короля
    x,y = second_group[0].x , second_group[0].y
    
    # шах этому королю
    Figs.check = False
    if animy_territory[y,x] != 0:
        Figs.check = second_group[0] # Объявление шаха
            
        

# визуал
def draw_figs(): #шахматное поле
    # рисую шахматное поле
    draw_img('chess',f'{color}_board',sc,(560,0))

    # рисую фигуры
    all_figs = Figs.my_troops + Figs.animy_troops
    for i in all_figs:   
        draw_img('chess',i.name,sc,(560+i.x*85,i.y*85))
    
def draw_scoreboard(): # рисую табло
    table = load_img('chess','scoreboard')#sc,(85,85)
    cords = (95,170)

    font = pygame.font.SysFont('arial',70)
    for i in range(len(score)):
        text = font.render(score[i],True,(0,0,0))
        
        k = 31 if i > 1 else 0 # оступ между полями
        
        table.blit(text,text.get_rect(center = (42+k+i*85,40)))
    
    sc.blit(table,cords)

def draw_message(mes):
    '''
    mes - тип сообщения\n
    '''
    # необходимые константы
    col = turn
    
    def get_replicas(path,name): # получить список реплик по указанному пути
        replicas = []
        with open(f'{Path_dir}/data/chess_mode/replicas/{name}/{path}.txt',encoding='utf-8') as file: # реплики
            replic = []
            for i in file:
                i = i[:-1]
                if i == '':
                    replicas.append(replic)
                    replic = []
                else:
                    replic.append(i)
        return replicas
    
      
    # получить реплику
    if mes == 'company': #В компании, определенную
        replic = get_replicas('company',ex)[Company.mes_ind]    
    else: # случайную
        replic = choice(get_replicas(mes,AI.name))
    
    # полотно
    surf = get_unvis_surf((434,228))
    
    # фон фигуры
    col_b = (181,136,99) if col == 'B' else (240,217,181)
    sur_b = pygame.Surface((85,85))
    sur_b.fill(col_b)
    surf.blit(sur_b,(30,31))
    
    # рисую фигуру
    if replic[0][0] not in ('k','q','g','h','r','p'):
        figure = 'k'
        name = AI.name
    else:
        figure = replic[0][0]
        name = replic[0][0]
        replic.pop(0)
        
    draw_img('chess',f'{col}{figure}',surf,(30,31))
             
    # рисую рамку
    draw_img('chess','message',surf)
    
    # шрифт Monotype Corsiva/Gabriola/DS-Digital
    font = pygame.font.SysFont('Gabriola',35)
    
    # Фигура, которая с нами говорит
    figs = {'k':'Король',
            'q':'Ферзь',
            'g':'Слон',
            'h':'Конь',
            'r':'Ладья',
            'p':'Пешка',
            'Junior' : 'Малыш',
            'Weasel' : 'Проныра',
            'Robot' : 'Робот',
            'Bully' : 'Громила',
            'Tricky' : 'Хитрец',
            'Biter' : 'Кусала',
            'Smarty' : 'Умник',
            'Fierce' : 'Лютый',
            'Hardy' : 'Сильнейший'}
    
    figure = font.render(figs[name],True,(0,0,0))
    surf.blit(figure,(269,181))
    
    # реплика
    height = figure.get_rect().height
    for i in range(len(replic)):
        rep = font.render(replic[i],True,(0,0,0))
        
        # рисую строчку
        if i < 3:
            surf.blit(rep,(144,26+i*height))
        else:
            surf.blit(rep,(98,131))
    
    # рисую полотно
    sc.blit(surf,(80,295))
    pygame.display.flip()
    
    # убрать сообщение
    set_cycle('space')
    
def draw_timer():
    # создать шрифт
    font = pygame.font.SysFont('DS-Digital',85)

    for i in range(2):
        if timers[i] != -1: #есть секунды
            # секунды перевожу в минуты
            min = timers[i]//60
            min = f'0{min}' if min<10 else str(min)
            # остаток секунд
            sec = timers[i]%60
            sec = f'0{sec}' if sec<10 else str(sec)
        else:
            min,sec = '00','00'
        
        # полотно
        surf = load_img('chess','timer')
        
        # нарисовать часы
        timer = font.render(f'{min}:{sec}',True,(0,0,0))
        surf.blit(timer,(8, 9))
        
        # прозрачность
        if turn == color[0]:
            if i == 0:
                surf.set_alpha(50)
            else:
               surf.set_alpha(150) 
        else:
            if i == 1:
                surf.set_alpha(50)
            else:
               surf.set_alpha(150) 
            
        
        # отрисовать полотно
        draw_img('chess',f'timer_back_{i}',sc,(0,604*i))
        sc.blit(surf,(10,(10,608)[i]))

def draw_company(*inds):
    for i in inds:
        Company.mes_ind = i
        draw_message('company')

    update_chess()
        
def update_chess(turn_hlter = True): #обновить дисплей
    draw_img('chess','background',sc)
    draw_scoreboard()
    draw_figs()
    draw_timer()
    
    if turn_hlter == True:
        highlighter()
    pygame.display.flip()

def highlighter(cells = None, col = None):
    global score
    surf = pygame.Surface((85,85))
    
    if path != None: # закрасить сделанный ход желтым
        # выделить ход
        surf.fill((155,242,0))
        surf.set_alpha(100)
        
        for i in path: # поле хайлайтер
            x,y = i
            sc.blit(surf,(560+x*85,y*85))
    
    elif len(score) > 0: # выделить ход
        surf.fill((0,255,0))
        surf.set_alpha(100)
        
        # поле хайлайтер
        x = LetToInd(score[0])
        y = NumToInd(score[1])
        sc.blit(surf,(560+x*85,y*85))
        
        if len(score)> 2: # 2 поле хайлайтер
            x2 = LetToInd(score[2])
            y2 = NumToInd(score[3])
            # пометить, можно ли пойти на это поле
            if (x2,y2) not in Figs.field_fig[y,x].get_av_cells():
                surf.fill((255,0,0))
                score = score[:2]
            else:
                surf.fill((0,255,0)) 
            
            
            sc.blit(surf,(560+x2*85,y2*85))
            
        if len(score) == 2: # доступные клетки
            draw_av_cells()
        
    # шах
    if Figs.check != False:
        animy_ter = Figs.territory[1] if Figs.check.name[0] == color[0] else Figs.territory[0]


        # поля, которые будут закрашены красным
        forbidden_cells = []
        
        Figs.check.set_aur()
        for i in Figs.check.aur:
            x,y = i
            if animy_ter[y,x] != 0:
                forbidden_cells.append(i)
        
        # рисую поля
        surf.fill((255,0,0))
        for i in forbidden_cells:
            x,y = i
            sc.blit(surf,(560+x*85,y*85))
        
        # крашу поле короля
        x,y = Figs.check.x,Figs.check.y
        sc.blit(surf,(560+x*85,y*85))
    
    # выделить определенные клетки
    if cells != None and type(col) == tuple:
        surf.fill(col)
        for i in cells:
            x,y = i
            sc.blit(surf,(560+x*85,y*85))
            
def draw_av_cells():
    # координаты фигуры
    x = LetToInd(score[0])
    y = NumToInd(score[1])

    fig = Figs.field_fig[y,x]
    if fig != None:
        av_cells = fig.get_av_cells()
        
        dote = load_img('chess','dote')
        dote.set_alpha(100)
        for i in av_cells:
            x,y = i
            sc.blit(dote,(560+x*85,y*85))

def draw_end():
    # создать шрифт
    font = pygame.font.SysFont('Gabriola',100)
    
    # полотно
    surf = load_img('chess','end')
    
    # Результат
    fin = {'win' : 'Победа',
            'defeat' : 'Поражение',
            'stalemate' : 'Ничья'}[end]
        
    # нарисовать результат
    fin = font.render(fin,True,(0,0,0))
    surf.blit(fin,fin.get_rect(center = (300,100)))
        
    draw_img('chess','background',sc)
    sc.blit(surf,(340, 260))
    pygame.display.flip()
    
    set_cycle('escape')
    draw_img('chess','background',sc)
    pygame.display.flip() 
  
  
  
# ввод
def mouse(but): # ввод через мышку
    global score
    if but == 'DOWN1':
        # получаю pos мышки
        pos = pygame.mouse.get_pos()
        
        # определяю на какое поле наведена мышка
        x,y = None,None
        
        b = 560
        for i in range(8): # пробегаю по x
            a = b
            b = a+85
            
            if pos[0] in range(a,b):
                x = i
        
        b = 0
        for i in range(8): # пробегаю по y
            a = b
            b = a+85
            
            if pos[1] in range(a,b):
                y = i
        
        # если мышка наведена на поле
        if x != None and y != None:
            # нумерация поля
            Li = 'abcdefgh' if color == 'White' else 'hgfedcba'
            Ni = 8 - y if color == 'White' else 1 + y
            LN = f'{Li[x]}{Ni}'
            
            # выбрать фигуру
            if Figs.field_fig[y,x] in Figs.my_troops:
                score = LN
            
            elif len(score) == 2: # передвинуть фигуру
                if Figs.field_fig[y,x] in Figs.animy_troops or Figs.field_fig[y,x] == None:
                    score += LN
            
            elif len(score) == 4: # поменять область, куда будет сдвинута фигрура 
                score = score[:2] + LN
            
            # обновить
            update_chess()
    
    elif but == 'space':
        if len(score) == 4:
            global path
            Ps = (LetToInd(score[0]),NumToInd(score[1]))
            Pe = (LetToInd(score[2]),NumToInd(score[3]))

            if Figs.field_fig[Ps[1],Ps[0]] in Figs.my_troops: # переставляю фигуру
                path = (Ps,Pe)
                moveFig()
            else:
                score = ''
    
    elif but == 'DOWN3':
        score = ''
        update_chess()

def editor():
    ai = ('Малыш','Проныра','Громила','Хитрец','Кусала','*Умник','*Лютый','*Сильнейший')
    ttime = ('5:00','2:00','1:30','1:00')
    xT = 0
    xAI = 0
    def update():
        surf = load_img('service','editor')
        # создать шрифт
        font = pygame.font.SysFont('Gabriola',32) 
        fontB = pygame.font.SysFont('Gabriola',50)
        
        # противник
        surf.blit(font.render('противник:',True,(0,0,0)),(137, 14))
        text = fontB.render(ai[xAI],True,(0,0,0))
        surf.blit(text,text.get_rect(center = (200,70)))
        
        # время
        surf.blit(font.render('время:',True,(0,0,0)),(166, 104))
        text = fontB.render(ttime[xT],True,(0,0,0))
        surf.blit(text,text.get_rect(center = (200,150)))
        
        # отрисовать
        sc.blit(surf,(440, 235))
        pygame.display.flip()
    
    
    # выбираю
    y = 0
    update()
    while 1:
        but = get_button()
        
        if but == 'return':
            break
        
        elif but in ('up','down'):
            b = {'up' : 0,
                 'down' : 1}
            
            y = b[but]
        
        elif but in ('right','left'):
            b = {'right' : 1,
                 'left' : -1}
            
            if y == 0:
                if xAI + b[but] in range(0,len(ai)):
                    xAI+= b[but]
            
                    update()   
            #
            else:
                if xT + b[but] in range(0,len(ttime)):
                    xT+= b[but]
            
                    update()
            
            
            
    
    # применить
    name_AI = {'Малыш':'Junior',
            'Проныра':'Weasel',
            'Робот':'Robot',
            'Громила':'Bully',
            'Хитрец':'Tricky',
            'Кусала':'Biter',
            'Умник':'Smarty',
            'Лютый':'Fierce',
            'Сильнейший':'Hardy'}
    AI.set_AI(name_AI[ai[xAI]])
    
    with open(f'{Path_dir}/data/chess_mode/timer.txt','w') as file: # таймер
        for i in range(2):
            file.write(('300\n','120\n','90\n','60\n')[xT])

        


# игры
def Checkmate_1(example = None):
    Figs.castling = False
    
    def select_ex(path):
        # получить список примеров по указанному пути
        exs = []
        for i in listdir(f'data/chess_mode/{path}'):
            exs.append(i[:-4])
        
        # получаю 25 примеров, думаю этого будет достаточно
        shuffle(exs)
        exs_sel = exs[:timers[1]//5]
        
        return exs_sel
    
    # сначала самое главное
    global mode,ex,timers
    mode = 'Chess&mate_1'
    AI.set_AI('Robot')
    set_timer()
    
    # примеры
    exs = select_ex('Chess&mate_1') if example == None else [example,]
    num = 0
    
    # подготовка
    ex = exs[num]
    update_data()
    set_new_ex()
    timers[0] = 70
    
    # прогружаю доску
    update_chess()
    
    # игра
    Run.update()
    t = 0
    while 1:
        clock.tick(30)
        # ходит ИИ
        if color[0] != turn:
            AI.makeMove()
            sleep(1)
            if Run.run == True: # робот сходил
                timers[0] += 1
                
                update_data()
                set_new_ex()
                update_chess()
                
            elif Figs.check == False: # пат
                timers[0] += 1
                 
                update_data()
                set_new_ex()
                update_chess()
                
            else:
                if num+1 <len(exs):
                    num += 1
                    ex = exs[num]
                    
                    timers[0] += 60
                    
                    update_data()
                    set_new_ex()
                    update_chess()
                    
                    Run.update()
                
                else:
                    break
                
        else: # хожу я 
            but = get_but_mouse()
            
            if but != None:
                if but== 'escape':
                    break
                
                elif but == 'p': #баговый пример
                    with open(f'{Path.cwd()}/data/chess_mode/bag_files/bad_exs.txt','a') as file:
                        file.write(f'{ex}\n')
                    
                    if timers[0] > 60:
                        timers[0] -= 60
                    
                    num += 1
                    ex = exs[num]
                    
                    update_data()
                    set_new_ex()
                    update_chess()
                    
                    Run.update()
                    
                    
                else:
                    mouse(but)
        
        # работа с таймером
        if t == 30:
            t = 0
            # вычитаю секунду только у себя
            if turn == color[0]:
                timers[1] -= 1
                # обнавляю таймер
                draw_timer()
                pygame.display.flip()
                
                # если время закончилось
                if timers[1] < 0:
                    draw_message('win')
                    break
                
        else:
            t += 1
    
    update_data()
        
        
    
    draw_img('chess','background',sc)
    pygame.display.flip()

def MiniFight():
    global mode, ex, turn, end
    Figs.castling = True
    # редактор
    editor()

    # случай блитз
    AI.low_time()

    # меняю мод
    mode = 'MiniFight'
    set_timer()
    
    # открываю файл
    ex = 'Q_Q'
    update_data()
    set_new_ex()
    
    # прогружаю доску
    update_chess()
    
                   
    
    
    # игра
    Run.update()
    t = 0
    end = 'defeat'
    while Run.run:
        clock.tick(30)
        
        # ходит ИИ
        if color[0] != turn:
            AI.makeMove()
        
                
        else: # хожу я 
            but = get_but_mouse()
            if but != None:
                if but== 'escape':
                    break
                
                else:
                    mouse(but)
        
            # работа с таймером
            if t == 30:
                t = 0
                # вычитаю секунду только у себя
                if turn == color[0]:
                    timers[1] -= 1
                    # обнавляю таймер
                    draw_timer()
                    pygame.display.flip()
                    
                    # если время закончилось
                    if timers[1] < 0:
                        draw_message('win')
                        break
                    
            else:
                t += 1

    
    draw_end()

def Regular_game():
    global mode, ex, turn, end
    Figs.castling = True
    editor()
    # AI.set_AI('Robot') #! ставлю робота 
    
    # случай блитз
    AI.low_time()

    # меняю мод
    mode = 'Regular_game'
    set_timer()
    
    # новые данные
    ex = 'All'#
    update_data()
    set_new_ex()
    

    # прогружаю доску
    update_chess()
    
                   
    # игра
    Run.update()
    t = 0
    end = 'defeat'
    while Run.run:
        clock.tick(30)
        
        # ходит ИИ
        if color[0] != turn:
            AI.makeMove()
        
                
        else: # хожу я 
            but = get_but_mouse()
            if but != None:
                if but== 'escape':
                    break
                
                else:
                    mouse(but)
        
            # работа с таймером
            if t == 30:
                t = 0
                # вычитаю секунду только у себя
                if turn == color[0]:
                    timers[1] -= 1
                    # обнавляю таймер
                    draw_timer()
                    pygame.display.flip()
                    
                    # если время закончилось
                    if timers[1] < 0:
                        draw_message('win')
                        break
                    
            else:
                t += 1

    
    draw_end()

def toss_up(): # жеребьевка игроков
    from Toss_up import Toss_up

    draw_img('chess','background',sc)
    def draw_plrs(): 
        # нарисовать комманды
        Sx = 128
        Sy = 176
        round_pairs = pairs[round_i]

        for ind_pair in range(len(round_pairs)): #отрисовываю пары
            surf = load_img('toss_up',f'surf_com_{rand_surf_com}') # сюрфа
            
            winer = wins[str(ind_pair+1)]
            
            # отрисовываю игроков
            Plrx = 50
            k = 0 # индекс игрока в этой паре
            for plr in round_pairs[ind_pair]:
                y = 20 if k == winer else 104
                
                if plll[plr] == 'robot': # это робот
                    draw_img('toss_up','robot',surf,(Plrx,y))
                else:
                    surf.blit(plll[plr].image,(Plrx,y))
                    # draw_img('caracters/128',,surf,)
                
                Plrx = 324
                k += 1
            
            # отрисовать surf и изменить координаты surf
            sc.blit(surf,(Sx,Sy))
            
            Sx += 522
            if Sx == 1172:
                Sx = 128
                Sy = 448
                
        pygame.display.flip()
        
        
    plll = Player.players.sprites()
    
    # если игроков меньше 3, отключить
    if len(plll) < 3:
        draw_img('toss_up','error',sc,(389, 285))
        pygame.display.flip()
        
        set_cycle('space')
        draw_img('chess','background',sc)
        pygame.display.flip()
    

    else: # игроков больше
        plll = plll + ['robot'] if len(plll)%2 == 1 else plll
        pairs = Toss_up(plll)
        del Toss_up # удаляю за ненадобностью 

        for round_i in range(3): # три раунда
            # * визуал
            wins = {}
            for i in range(len(pairs[0])): # количество пар
                wins[str(i+1)] = None
            
            # нарисовать раунд
            round = load_img('toss_up','round')
            
            font = pygame.font.SysFont('arial',70)
            text = font.render(f'{round_i+1} раунд',True,(0,0,0))
            
            round.blit(text,text.get_rect(center = (251, 75)))
            sc.blit(round, (389,0))
            
            
            # нарисовать комманды
            rand_surf_com = randint(1,2)
            draw_plrs()

            
            # * победители в партии
            comms = tuple(wins.keys())
            while 1:
                but = get_button()
                
                if but == 'space':
                    break
                
                elif but in comms:
                    
                    # выбрать победителя в паре
                    while 1:
                        but_i = get_button()
                        
                        if but_i in ('left','right'): # раздать победу
                            if but_i == 'left':
                                wins[but] = 0
                            else:
                                wins[but] = 1
                            
                            draw_plrs()
                            break
            
            
            # * выдать баллы победителям
            for i in comms:
                winer_pair = wins[i] # индекс победителя в партии
                
                if winer_pair != None: # есть победитель
                    ind_pl = pairs[round_i][int(i) - 1][winer_pair] # индекс игрока

                    if plll[ind_pl] != 'robot':
                        caracter = plll[ind_pl]
                        
                        if caracter.energy + 1 in range(0,6):
                            # дать балл и передвинуть
                            caracter.energy += 1
                            caracter.rect.y -= 64
                            
                            # сохранить изменения
                            with open(f'{Path_dir}\data\save\points.txt','w') as write:
                                for j in Player.players.sprites():
                                    write.write(str(j.energy)+'\n')
        
        # * конец
        draw_img('chess','background',sc)
        pygame.display.flip()
    
def Test_game():
    global mode, ex, turn, end
    Figs.castling = True
    
    AI.set_AI('Tricky')
    AI.spend_time = 'robt'
    AI.num_Check = 2


    # меняю мод
    mode = 'test_game'
    set_timer()
    
    # открываю файл
    ex = 'test2'
    update_data()
    set_new_ex()
    
    # прогружаю доску
    update_chess()
    
                   
    
    
    # игра
    Run.update()
    t = 0
    end = 'defeat'
    while Run.run:
        clock.tick(30)
        
        # ходит ИИ
        if color[0] != turn:
            AI.makeMove()
        
                
        else: # хожу я 
            but = get_but_mouse()
            if but != None:
                if but== 'escape':
                    break
                
                else:
                    mouse(but)
        
            # работа с таймером
            if t == 30:
                t = 0
                # вычитаю секунду только у себя
                if turn == color[0]:
                    timers[1] -= 1
                    # обнавляю таймер
                    draw_timer()
                    pygame.display.flip()
                    
                    # если время закончилось
                    if timers[1] < 0:
                        draw_message('win')
                        break
                    
            else:
                t += 1

    
    draw_end()


#   основной цикл
def main():
    draw_img('chess','background',sc)
    pygame.display.flip()
    global mode, ex, timers
    while 1:
        but = get_button()
        
        if but != None:
            # не доделано!!!
            if but == '1':
                Regular_game()
            
            elif but == '2':
                MiniFight()
            
            elif but == '3':
                Checkmate_1()
            
            elif but =='4':
                toss_up()
            
            elif but =='5':
                AI.blitz = True if AI.blitz == False else False

            elif but == 'escape':
                break    

if __name__ == '__main__':
    main()