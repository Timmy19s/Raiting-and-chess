

from pickle import dump
from Chess_mode import *

# меняю мод
mode = 'test_game'
name = 'test2' # задать название файла
set_timer()

# TODO путь
path = f'D:\python/rating\data\chess_mode/{mode}' # задать путь




# обновить
ex = 'editor'
update_data()
k = array([array(['ec' for i in range(8)]) for i in range(8)])
color = 'White'

# прогружаю доску
def update_ch():
   # рисую шахматное поле
   draw_img('chess','White_board',sc,(560,0))

   # рисую фигуры  
   for yi in range(8):
      for xi in range(8):
         n = k[yi,xi] 
         if n != 'ec':
            draw_img('chess',n,sc,(560+xi*85,yi*85))
   
   pygame.display.flip()


# игра
Run.update()
fig = None
update_ch()
while Run.run:
   clock.tick(30)
   
   # навел фигуру
   but = get_but_mouse()
   
   if but in ('escape','return'): # выйти
      break
   
   
   # ввод фигуры
   elif but in ('p','r','h','g','q','k'):
      fig = but
   
   elif but == 'l':
      fig = 'allp'
      
   elif but == 'backspace':
      fig = None
   
   # поставить фигуру  
   elif but in ('DOWN1','DOWN3'):
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
            # поставить пешку
            if fig != None:
               if len(fig) == 1:
                  if but == 'DOWN1':
                     k[y,x] = f'W{fig}'
                  else:
                     k[y,x] = f'B{fig}'
               
               else:
                  if but == 'DOWN1':
                     figs = 'Wp'
                     y = 6
                  else:
                     figs = 'Bp'
                     y = 1
                  
                  for i in range(8):
                     k[y,i] = figs
      
               
            
            else:
               k[y,x] = 'ec'
                  

            # прогружаю доску
            update_ch()
   

pygame.quit()
if but == 'return': # записать
   name = input('название:::') if name == None else name
   

   with open(f'{path}/{name}.txt','wb') as file:
         dump((color,k),file)  
   
   print('записано\n')       
        