import numpy as np

def game_core_v4(secret_number, show_path=False):
    """Попытаться угадать присланное число по правилам Игры и посчитать Попытки.
    
    Именнованные аргументы:
    secret_number -- число которое загадал Вода
    show_path -- булева - показывать ли в результате путь из ПредположенныхЧисел
                 которые придумывал Игрок (default False)
    
    
    Правила Игры:
    =============
    В эту Игру играют двое: Вода и Игрок.
    Вот какие Ходы им разрешено делать и в каком по порядке:
    1. Вода - загадывает целое СекретноеЧисло в интервале [1; 100]. После этого,
    Ход переходит к Игроку.
    2. Игрок - называет вслух одно ПредположенноеЧисло из интервала [1; 100] и
    Вода сразу честно оглашает ему один из трёх исходов, который подходит под
    ситуацию:
    - ПредположенноеЧисло меньше СекретногоЧисла!
    - ПредположенноеЧисло равно СекретномуЧислу! Победа!
    - ПредположенноеЧисло больше СекретногоЧисла!
    После этого оглашения, считается что Игрок сделал одну Попытку.
    3. Ход 2 повторяется сколько угодно раз - либо до того момента как Игрок не
    Победит, либо пока он не признает Поражение.
    4. Если Игрок Победил, то количество Попыток считается и чем оно меньше -
    тем большим поводом для Гордости оно служит :)
    
    Стратегия:
    ==========
    Игрок может придерживаться какого-то алгоритма чтобы увеличить свои шансы на
    быструю победу!
    
    Эта функция эмулирует один такой алгоритм поведения игрока чтобы проверить
    его жизнеспособность.
    
    Идея/разработка:
    ================
    Мы хотим победить *побыстрее*. Поэтому задав один вопрос хочется получить
    как можно полезных ответов. Экономичность движений - драгоценна! 
    
    Если у нас три исхода - меньше, равно, больше, то самое полезное мы можем
    получить в случае:
    
    oXo
    123
    
    если мы зададим вопрос про число x (=2) то вот что будут означать ответы:
    - МЕНЬШЕ будет означать что СекретноеЧисло = 1.
    - РАВНО будет означать что СекретноеЧисло = 2.
    - БОЛЬШЕ будет означать что СекретноеЧисло = 3.
    
    Наращиваем сложность - берём два oxo. По середине вставляем между ними один
    единственный элемент:
    
    oooXooo
    1  4  7
    
    - МЕНЬШЕ будет означать что СекретноеЧисло - одно из 123 и можно
      воспользоваться алгоритмом предыдущей сложности чтобы его найти за один
      вопрос.
    - РАВНО будет означать что СекретноеЧисло = 4.
    - БОЛЬШЕ будет означать что СекретноеЧисло - одно из 567 и можно
      воспользоваться алгоритмом предыдущей сложности чтобы его найти за один
      вопрос.
    
    Если экстраполировать это простейшее поведение дальше, то получается
    повторящийся алгоритмический рисунок:
    
    oXo
    123
    
    oooXooo
    1  4  7
    
    oooooooXooooooo
    1      8      15
    
    oooooooooooooooXooooooooooooooo
    1              16             31
    
    oooooooooooooooooooooooooooooooXooooooooooooooooooooooooooooooo
    1                              32                             63
    
    ...
    
    Т.е.
    1: [1; 3]   X=2=2**1
    2: [1; 7]   X=4=2**2
    3: [1; 15]  X=8=2**3
    4: [1; 31]  X=16=2**4
    5: [1; 63]  X=32=2**5
    6: [1; 127] X=64=2**6 - Как раз нам подходит чтобы угадать число [1; 100].
    
    Отсюда алгоритм - начинаем игру с 2**6.
    - МЕНЬШЕ тогда пробуем (2**6 - 2**5)
    - РАВНО успех - ПОБЕДА
    - БОЛЬШЕ тогда пробуем (2**6 + 2**5)
    
    Если мы ещё не достигли успеха - просто понижаем степень.
    
    [1; 127] вылезает за пределы [1; 100] поэтому можно сократить Попытки, если
    у тебя ПредположенноеЧисло вылезает за пределы [1; 100], НЕ ОГЛАШАТЬ его
    вслух, но считать что результат от Воды был МЕНЬШЕ и продолжить двигаться по
    алгоритму, пока опять ПредположенноеЧисло не попадёт вновь в интервал.
    
    На всякий случай чтобы не впасть в рекурсию - ставим себе ограничение если
    мы почему-то посчитали ПредположенноеЧисло 12 раз и до сих пор не угадали
    результат - то надо Сдаться.
    """
    
    limit_min = 1
    limit_max = 100
    attempt_count = 0
    path = [] # Вот это нам может пригодится для отладки.
    
    
    def declare(guess_number):
        """Огласить догадку вслух, истратив Попытку Игрока."""
        attempt_count += 1
        
        if guess_number < secret_number:
            return 'less'
        elif guess_number == secret_number:
            return 'equal'
        else:
            return 'more'
    
    
    # С точки зрения цикла можно считать что это - начальное положение
    # алгоритма.
    is_win = 0
    guess_number = 0
    declaration = 'less' # ПредположенноеЧисло ... чем СекретноеЧисло.
    power = 6
    despair_level = 0 # Если Отчаянье достигнет 12 - Игрок сдастся.
    while despair_level < 12:
        
        despair_level += 1
        
        if declaration == 'equal':
            result['is_win'] = True
            break
        if declaration == 'less':
            guess_number += 2**power
        if declaration == 'more':
            guess_number -= 2**power
        
        path.append(guess_number)
        
        power -= 1
        
        # Если мы выбились за пределы.
        if guess_number < limit_min:
            declaration = 'less'
            continue
        if guess_number > limit_max:
            declaration = 'more'
            continue
        
        declaration = declare(guess_number)
    
    result = {
        'is_win': is_win,
        'attempt_count': attempt_count,
    }
    
    if show_path:
        result['path'] = path
    
    return result


# def score_game(game_core):
#     """Вернуть результаты проверки алгоритма угадывания.
# 
#     Запускаем игру 1000 раз, чтобы узнать, как быстро игра угадывает число.
#     """
#     results_list = []
# 
#     # Фиксируем RANDOM SEED, чтобы ваш эксперимент был воспроизводим!
#     np.random.seed(1)
#     random_array = np.random.randint(1,101, size=(1000))
# 
#     for number in random_array:
#         results_list.append(game_core(number))
# 
#     score = int(np.mean(success_count_list))
#     print(f'Ваш алгоритм угадывает число в среднем за {score} попыток')
#     return(score)
