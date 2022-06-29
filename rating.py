from WWP import *

    
# создаю игроков
set_new_Pl()
Player.arrange()

Player.draw_caracters()

Run.update()
while Run.run:
    button = get_button()
    
    if button == 'escape': # выход
        Run.stop()
    
    elif button in Player.pl_keys:
        Player.give_energy(button)
    
    elif button in ('up','down'):
        if button == 'up':
            Player.tool = 1
        else:
            Player.tool = -1
    
    elif button == 'd': # дать всем по баллу за дисциплину
        for i in range(len(Player.players)):
            Player.give_energy(i)
    
    elif button == '`': # добавить игрока
        set_caracters(1)
        Player.draw_caracters()
    
    elif button == 'tab': # перераспределить
        Player.arrange()
        Player.draw_caracters()
    
    elif button == 'c':
        from Chess_mode import toss_up
        toss_up()
        del toss_up
        Player.draw_caracters() 
        
    
    # проверить, правда ли хочу выйти
    if Run.run == False:
        # TODO визуал нужно подготовить
        draw_img('service','background',sc)
        draw_img('service','out',sc,(415, 260))
        
        pygame.display.flip()
        while 1:
            but = get_button()
            
            if but == 'return': # выйти
                break
            
            elif but == 'escape': # вернуться
                Run.update()
                Player.draw_caracters()
                break
                
            
            