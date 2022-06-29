from random import choice
from numpy import array

def Toss_up(pls):
    fail = True
    while fail:
        fail = False

        # матрица пар
        pairs = []
        lenth_str = len(pls) - 1
        for i in range(lenth_str): # пробегаю по каждому игроку, кроме последнего
            string = ['av'] * len(pls[i + 1:])# доступные пары в строке
            
            string += ['00'] * (lenth_str - len(string))
            
            pairs.append(array(string))
        pairs = array(pairs)

        res_prs = []
        for round in range(3):
            choiced_prs = []
            # ищу пары
            for i in range(len(pls)//2):
                # доступные пары
                av_pairs = []
                for i in range(lenth_str): # количество столбцов и строк одинаково
                    for j in range(lenth_str):
                        if pairs[i,j] == 'av':
                            av_pairs.append((i, j + i + 1))


                # выбираю пару и удаляю ее из матрицы
                try:
                    pair = choice(av_pairs)
                except:
                    fail = True

                y = pair[0]
                x = pair[1] - y - 1
                pairs[y,x] = '00'
                choiced_prs.append(pair)


                # делаю недоступными пары c этими людьми
                for xi in range(lenth_str): # строки
                    if pairs[y,xi] == 'av': #строка y
                        pairs[y,xi] = 'fb'

                    if pair[1] != lenth_str and pairs[pair[1],xi] == 'av': # строка x
                        pairs[pair[1],xi] = 'fb'

                for i in range(lenth_str): #диагонали
                    # первое число
                    xi = pair[0] - i - 1
                    if xi > -1 and pairs[i,xi] == 'av':
                        pairs[i,xi] = 'fb'
                    
                    # второе число
                    xi = pair[1] - i - 1
                    if pairs[i,xi] == 'av':
                        pairs[i,xi] = 'fb'
            
            
            # пара с ботом идет в конец
            for pr in choiced_prs:
                i = choiced_prs.index(pr)
                if pr[1] == len(pls) - 1 and pls[pr[1]] == 'robot' and i != len(choiced_prs) - 1:
                    choiced_prs[i],choiced_prs[-1] = choiced_prs[-1],choiced_prs[i]
                    
            # Выбранные пары бросаю в res
            res_prs.append(choiced_prs)
            
            
            # обновляю матрицу
            for i in range(lenth_str): # количество столбцов и строк одинаково
                for j in range(lenth_str):
                    if pairs[i,j] == 'fb':
                        pairs[i,j] = 'av'

    return res_prs


