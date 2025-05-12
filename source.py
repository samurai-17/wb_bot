import telebot
from telebot import types
import sqlite3
import time
import random
import dotenv
import os

dotenv.load_dotenv()
token = os.getenv("token_tg")
bot = telebot.TeleBot(token)

@bot.message_handler(commands = ["information"])
def information(message):
    bot.send_message(message.chat.id, "Привет! Я создан для того, чтобы Вы играли и копили внутриигровую валюту Coins🟡. Топ 10 игроков по количеству 🟡 получат призы.")

@bot.message_handler(commands= ["start"])
def start(message):
    name = message.from_user.username
    id = message.chat.id
    coins = 0
    s_try = time.time() - (60*60*24)
    l_try = time.time()

    conn = sqlite3.connect('data.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (id int PRIMARY KEY, name varchar(50), coins int, s_try int, l_try int, pvp_b int, pvp_o int, pvp_o_f varchar, id_of_host int, id_of_unhost int, in_game int)')

    conn.commit()
    cur.close()
    conn.close()

    conn = sqlite3.connect('data.sql')
    cur = conn.cursor()

    get_id = None
    for i in cur.execute(f"SELECT s_try FROM users WHERE id = '{message.chat.id}'"):
        get_id = i[0]
    if get_id == None:
        cur.execute("INSERT INTO users (id, name, coins, s_try, l_try, in_game) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (id, name, coins, s_try, l_try, 0))

    conn.commit()
    cur.close()
    conn.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard= True)
    button_1 = types.KeyboardButton("Coins 🟡")
    # В разработке
    # button_3 = types.KeyboardButton("Реферальная система")
    button_2 = types.KeyboardButton("Игры 🎮")
    markup.row(button_1, button_2)
    # markup.row(button_3)
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}", reply_markup=markup)

@bot.message_handler(content_types=["text"])
def function(message):
    if (message.text == "Coins 🟡"):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Узнать количество Сoins 🟡", callback_data="quantity_of_coins"))
        markup.add(types.InlineKeyboardButton("Получить ежедневный Сoin 🟡", callback_data="give_coin"))
        bot.reply_to(message, "Твои Coins 🟡", reply_markup=markup)
# В разработке
    # elif (message.text == "Реферальная система"):
    #     markup = types.InlineKeyboardMarkup()
    #     markup.add(types.InlineKeyboardButton("Узнать количество рефералов", callback_data="quantity_of_refs"))
    #     markup.add(types.InlineKeyboardButton("Поделиться", callback_data = "Share"))
    #     bot.reply_to(message, "Реферальная система", reply_markup=markup)
    elif (message.text == "Игры 🎮"):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Баскетбол 50🟡", callback_data="basketball"))
        markup.add(types.InlineKeyboardButton("Орлок 100🟡", callback_data="orlock"))
        bot.reply_to(message, "Каталог игр", reply_markup=markup)
# Сделано для игры с другом
    elif (message.text[0] == "@"):

        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()

        cur.execute(f"UPDATE users SET pvp_o = 1 WHERE id = '{message.chat.id}'")
        cur.execute(f"UPDATE users SET pvp_o_f = '{message.text[1:]}' WHERE id = '{message.chat.id}'")

        conn.commit()
        cur.close()
        conn.close()

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Продолжить", callback_data="orlock_start"))
        bot.reply_to(message, "Нажми на кнопку!", reply_markup=markup)
# Конец работы

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == "give_coin":
        balance = 0
        success_try = 0

        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()

        for i in cur.execute(f"SELECT s_try FROM users WHERE id = '{callback.message.chat.id}'"):
            success_try = i[0]

        last_try = time.time()

        if(((last_try - success_try) >= (60*60*24))):
            for i in cur.execute(f"SELECT coins FROM users WHERE id = '{callback.message.chat.id}'"):
                balance = i[0]

            send_dice = bot.send_dice(callback.message.chat.id, "")
            balance += send_dice.dice.value * 100

            cur.execute(f"UPDATE users SET coins = {balance} WHERE id = '{callback.message.chat.id}'")
            cur.execute(f"UPDATE users SET s_try = {last_try} WHERE id = '{callback.message.chat.id}'")
            cur.execute(f"UPDATE users SET l_try = {last_try} WHERE id = '{callback.message.chat.id}'")
            time.sleep(5)
            bot.send_message(callback.message.chat.id, f"Coin 🟡 начислен в твоей копилке {balance} coins")
        else:
            cur.execute(f"UPDATE users SET l_try = {last_try} WHERE id = '{callback.message.chat.id}'")
            for i in cur.execute(f"SELECT s_try FROM users WHERE id = '{callback.message.chat.id}'"):
                success_try = i[0]
            raznica = success_try + (60*60*24) - last_try
            raznica = int((str(raznica).split("."))[0])
            h = raznica//3600
            m = (raznica%3600)//60
            if(h < 1):
                bot.send_message(callback.message.chat.id, f"Подожди еще {m} минут!")
            elif(h == 1 or h == 21):
                bot.send_message(callback.message.chat.id, f"Подожди еще {h} час и {m} минут!")
            elif(h==2 or h==3 or h==4 or h==22 or h==23 or h==24):
                bot.send_message(callback.message.chat.id, f"Подожди еще {h} часа и {m} минут!")
            else:
                bot.send_message(callback.message.chat.id, f"Подожди еще {h} часов и {m} минут!")

        conn.commit()
        cur.close()
        conn.close()

    elif callback.data == "quantity_of_coins":
        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()

        for i in cur.execute(f"SELECT coins FROM users WHERE id = '{callback.message.chat.id}'"):
            balance = i[0]

        conn.commit()
        cur.close()
        conn.close()

        bot.send_message(callback.message.chat.id,f"Под твоей подушкой {balance} Coins 🟡")

    elif callback.data == "basketball":

        id_of_enemy = None
        in_game = 0

        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()
        balance = None
        for i in cur.execute(f"SELECT coins FROM users WHERE id = '{callback.message.chat.id}'"):
            balance = i[0]
        for i in cur.execute(f"SELECT in_game FROM users WHERE id = '{callback.message.chat.id}'"):
            in_game = i[0]
        if balance < 50:
            bot.send_message(callback.message.chat.id, "У тебя не хватает Coins 🟡 :с")
        elif in_game != 0:
            bot.send_message(callback.message.chat.id, "Вы уже в игре! Вам необходимо доиграть партию!")
        else:
            cur.execute(f"UPDATE users SET pvp_b = 1 WHERE id = '{callback.message.chat.id}'")

            for i in cur.execute(f"SELECT id FROM users WHERE id != '{callback.message.chat.id}' and pvp_b = 1"):
                id_of_enemy = i[0]
                break
            conn.commit()
            cur.close()
            conn.close()

            if (id_of_enemy == None):
                bot.send_message(callback.message.chat.id, "Игроков нет, но Вы в поиске!")
            else:

                conn = sqlite3.connect('data.sql')
                cur = conn.cursor()
                cur.execute(f"UPDATE users SET in_game = 1 WHERE id = '{callback.message.chat.id}'")
                cur.execute(f"UPDATE users SET in_game = 1 WHERE id = '{id_of_enemy}'")
                cur.execute(f"UPDATE users SET pvp_b = 0 WHERE id = '{callback.message.chat.id}'")
                cur.execute(f"UPDATE users SET pvp_b = 0 WHERE id = '{id_of_enemy}'")
                conn.commit()
                cur.close()
                conn.close()

                balance_1 = None
                balance_2 = None
                conn = sqlite3.connect('data.sql')
                cur = conn.cursor()
                for i in cur.execute(f"SELECT coins FROM users WHERE id = '{callback.message.chat.id}'"):
                    balance_1 = i[0]
                for i in cur.execute(f"SELECT coins FROM users WHERE id = '{id_of_enemy}'"):
                    balance_2 = i[0]
                send_dice_1 = bot.send_dice(callback.message.chat.id, "🏀")
                send_dice_2 = bot.send_dice(id_of_enemy, "🏀")
                time.sleep(5)
                player_1 = send_dice_1.dice.value
                player_2 = send_dice_2.dice.value
                if player_1 > 3:
                    player_1 = 1
                else:
                    player_1 = 0
                if player_2 > 3:
                    player_2 = 1
                else:
                    player_2 = 0
                if player_1 == player_2:
                    bot.send_message(callback.message.chat.id, f"Ничья, в твоем распоряжении {balance_1} Coins 🟡")
                    bot.send_message(id_of_enemy, f"Ничья, в твоем распоряжении {balance_2} Coins 🟡")
                elif player_1 > player_2:
                    bot.send_message(callback.message.chat.id, f"Победа, в твоем распоряжении {balance_1 + 50} Coins 🟡")
                    bot.send_message(id_of_enemy, f"Поражение, в твоем распоряжении {balance_2 - 50} Coins 🟡")
                    cur.execute(f"UPDATE users SET coins = {balance_1 + 50} WHERE id = '{callback.message.chat.id}'")
                    cur.execute(f"UPDATE users SET coins = {balance_2 - 50} WHERE id = '{id_of_enemy}'")
                else:
                    bot.send_message(callback.message.chat.id, f"Поражение, в твоем распоряжении {balance_1 - 50} Coins 🟡")
                    bot.send_message(id_of_enemy, f"Победа, в твоем распоряжении {balance_2 + 50} Coins 🟡")
                    cur.execute(f"UPDATE users SET coins = {balance_2 + 50} WHERE id = '{id_of_enemy}'")
                    cur.execute(f"UPDATE users SET coins = {balance_1 - 50} WHERE id = '{callback.message.chat.id}'")
                cur.execute(f"UPDATE users SET in_game = 0 WHERE id = '{callback.message.chat.id}'")
                cur.execute(f"UPDATE users SET in_game = 0 WHERE id = '{id_of_enemy}'")
                conn.commit()
                cur.close()
                conn.close()

# Пользователь выбирает играть с другом или случайно
    elif callback.data == "orlock":

        in_game = 0
        balance = None

        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()
        for i in cur.execute(f"SELECT coins FROM users WHERE id = '{callback.message.chat.id}'"):
            balance = i[0]
        for i in cur.execute(f"SELECT in_game FROM users WHERE id = '{callback.message.chat.id}'"):
            in_game = i[0]
        conn.commit()
        cur.close()
        conn.close()
        if balance < 100:
            bot.send_message(callback.message.chat.id, "У тебя не хватает Coins 🟡 :с")
        elif in_game != 0:
            bot.send_message(callback.message.chat.id, "Вы уже в игре! Вам необходимо доиграть партию!")
        else:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("С другом", callback_data="friend"))
            markup.add(types.InlineKeyboardButton("Случайно", callback_data="orlock_start"))
            markup.add(types.InlineKeyboardButton("Некорректно ввел ник друга", callback_data="delete_friend"))
            markup.add(types.InlineKeyboardButton("Правила игры", callback_data="manual"))
            bot.send_message(callback.message.chat.id, "Выбери тип подключения", reply_markup=markup)

    elif callback.data == "friend":
        bot.send_message(callback.message.chat.id, "Напиши ник своего друга с @ в начале!")

    elif callback.data == "delete_friend":
        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()

        cur.execute(f"UPDATE users SET pvp_o = '{''}' WHERE id = '{callback.message.chat.id}'")
        cur.execute(f"UPDATE users SET pvp_o_f = '{''}' WHERE id = '{callback.message.chat.id}'")

        conn.commit()
        cur.close()
        conn.close()

    elif callback.data == "manual":
        bot.send_message(callback.message.chat.id, "Игра состоит из двух раундов, победитель определяется по количеству единиц здоровья (у кого больше, тот и выиграл). В первом раунде Вам будут 5 карт на выбор, необходимо выбрать две карточки, чтобы перейти к сражению. Карты Аткаки ⚔️ и 🏹 наносят одну единицу урона противнику, в случае, если противник не парирует атаку Картами Парирования 🛡️ и 🪖. Правила парирования: Карта Парирования 🛡️ отражает Карту Атаки 🏹, Карта Парирования 🪖 отражает Карту Атаки ⚔️. Также есть Карта Энергии ⚡️, после избрания двух карт первого раунда Вам предложат распорядиться Энергией ️️ ⚡️, если Вы ее выбрали. Распорядиться Энергией ⚡️ можно с помощью заклинания. Есть два вида заклинаний: Ярость и Мудрость. Ярость отниает у противника столько единиц здоровья, сколько у Вас было Энергии ⚡️. Мудрость прибавляет Вам столько единиц здоровья, сколько у Вас было Энергии ⚡️. Однако для успешности заклинания Вам нужно пройти проверку. Проходите проверку - заклинание осущиствляется, в ином случае Энергия ⚡️ сгорает. Во втором раунде Вам будут предложены 3 карты на выбор, необходимо выбрать две карточки, чтобы перейти к сражению. Во втором раунде Вы не встретите Карту Энергии ⚡️.")
# Конец работы

    # Начало игры
    elif callback.data == "orlock_start":

        id_of_enemy = None
        readiness = None

        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()
        balance = None
        for i in cur.execute(f"SELECT coins FROM users WHERE id = '{callback.message.chat.id}'"):
            balance = i[0]
        conn.commit()
        cur.close()
        conn.close()
        if balance < 100:
            bot.send_message(callback.message.chat.id, "У тебя не хватает Coins 🟡 :с")
        else:
# Добавлены дополнительные проверки на то, играет пользователь с другом или нет
            conn = sqlite3.connect('data.sql')
            cur = conn.cursor()
            for i in cur.execute(f"SELECT pvp_o FROM users WHERE id = '{callback.message.chat.id}'"):
                readiness = i[0]
            if readiness == 1:
                for i in cur.execute(f"SELECT id FROM users WHERE pvp_o_f = '{callback.message.chat.username}' and pvp_o = 1"):
                    id_of_enemy = i[0]
                if id_of_enemy != None:
                    cur.execute(f"UPDATE users SET pvp_o_f = '{''}' WHERE id = '{callback.message.chat.id}'")
                    cur.execute(f"UPDATE users SET pvp_o_f = '{''}' WHERE id = '{id_of_enemy}'")
            else:
                cur.execute(f"UPDATE users SET pvp_o = 1 WHERE id = '{callback.message.chat.id}'")
                for i in cur.execute(f"SELECT id FROM users WHERE id != '{callback.message.chat.id}' and pvp_o = 1 and pvp_o_f = '{''}'"):
                    id_of_enemy = i[0]
                    break

            conn.commit()
            cur.close()
            conn.close()
# Работы окончены
            if (id_of_enemy == None):
                bot.send_message(callback.message.chat.id, "Игрока нет, но Вы в ожидании!")
            else:
                host_id = 0
                conn = sqlite3.connect('data.sql')
                cur = conn.cursor()
                cur.execute(f"UPDATE users SET in_game = 1 WHERE id = '{callback.message.chat.id}'")
                cur.execute(f"UPDATE users SET in_game = 1 WHERE id = '{id_of_enemy}'")
                cur.execute(f"UPDATE users SET pvp_o = 0 WHERE id = '{callback.message.chat.id}'")
                cur.execute(f"UPDATE users SET pvp_o = 0 WHERE id = '{id_of_enemy}'")
                cur.execute(f"UPDATE users SET id_of_host = '{callback.message.chat.id}' WHERE id = '{id_of_enemy}'")
                cur.execute(f"UPDATE users SET id_of_host = '{callback.message.chat.id}' WHERE id = '{callback.message.chat.id}'")
                cur.execute(f"UPDATE users SET id_of_unhost = '{id_of_enemy}' WHERE id = '{id_of_enemy}'")
                cur.execute(f"UPDATE users SET id_of_unhost = '{id_of_enemy}' WHERE id = '{callback.message.chat.id}'")
                for i in cur.execute(f"SELECT id_of_host FROM users WHERE id = '{callback.message.chat.id}'"):
                    host_id = i[0]
                conn.commit()
                cur.close()
                conn.close()

                conn = sqlite3.connect('orlock.sql')
                cur = conn.cursor()
                cur.execute('CREATE TABLE IF NOT EXISTS users (id_of_host int, P1_cards varchar, P2_cards varchar, Deck_1 varchar, Deck_2 varchar, P1_health int, P2_health int, P1_bonus int, P2_bonus int, Continue int)')
                cur.execute("INSERT INTO users (id_of_host) VALUES ('%s')" % (callback.message.chat.id))
                cur.execute(f"UPDATE users SET Continue = {0} WHERE id_of_host = '{host_id}'")
                cur.execute(f"UPDATE users SET P1_health = {3} WHERE id_of_host = '{host_id}'")
                cur.execute(f"UPDATE users SET P2_health = {3} WHERE id_of_host = '{host_id}'")
                cur.execute(f"UPDATE users SET P1_bonus = {0} WHERE id_of_host = '{host_id}'")
                cur.execute(f"UPDATE users SET P2_bonus = {0} WHERE id_of_host = '{host_id}'")
                conn.commit()
                cur.close()
                conn.close()

                deck_1_mas = []
                deck_1 = ""
                for i in range(5):
                    a = random.randint(1, 5)
                    deck_1 += str(a)
                    if (a == 1):
                        deck_1_mas.append("⚔️")
                    if (a == 2):
                        deck_1_mas.append("🛡️")
                    if (a == 3):
                        deck_1_mas.append("🏹")
                    if (a == 4):
                        deck_1_mas.append("🪖")
                    if (a == 5):
                        deck_1_mas.append("⚡️")

                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton((deck_1_mas[0]), callback_data="p1_card_1"))
                markup.add(types.InlineKeyboardButton((deck_1_mas[1]), callback_data="p1_card_2"))
                markup.add(types.InlineKeyboardButton((deck_1_mas[2]), callback_data="p1_card_3"))
                markup.add(types.InlineKeyboardButton((deck_1_mas[3]), callback_data="p1_card_4"))
                markup.add(types.InlineKeyboardButton((deck_1_mas[4]), callback_data="p1_card_5"))
                bot.send_message(callback.message.chat.id, "Игра началась, выбери 2 карточки", reply_markup=markup)

                deck_2_mas = []
                deck_2 = ""
                for i in range(5):
                    a = random.randint(1, 5)
                    deck_2 += str(a)
                    if (a == 1):
                        deck_2_mas.append("⚔️")
                    if (a == 2):
                        deck_2_mas.append("🛡️")
                    if (a == 3):
                        deck_2_mas.append("🏹")
                    if (a == 4):
                        deck_2_mas.append("🪖")
                    if (a == 5):
                        deck_2_mas.append("⚡️")

                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton((deck_2_mas[0]), callback_data="p2_card_1"))
                markup.add(types.InlineKeyboardButton((deck_2_mas[1]), callback_data="p2_card_2"))
                markup.add(types.InlineKeyboardButton((deck_2_mas[2]), callback_data="p2_card_3"))
                markup.add(types.InlineKeyboardButton((deck_2_mas[3]), callback_data="p2_card_4"))
                markup.add(types.InlineKeyboardButton((deck_2_mas[4]), callback_data="p2_card_5"))
                bot.send_message(id_of_enemy, "Игра началась, выбери 2 карточки", reply_markup=markup)
                bot.send_message(id_of_enemy, f"Карты на выбор противника: {deck_1_mas[0]} {deck_1_mas[1]} {deck_1_mas[2]} {deck_1_mas[3]} {deck_1_mas[4]}")
                bot.send_message(callback.message.chat.id, f"Карты на выбор противника: {deck_2_mas[0]} {deck_2_mas[1]} {deck_2_mas[2]} {deck_2_mas[3]} {deck_2_mas[4]}")

                host_id = None
                conn = sqlite3.connect('data.sql')
                cur = conn.cursor()
                for i in cur.execute(f"SELECT id_of_host FROM users WHERE id = '{callback.message.chat.id}'"):
                    host_id = i[0]
                conn.commit()
                cur.close()
                conn.close()

                conn = sqlite3.connect('orlock.sql')
                cur = conn.cursor()
                cur.execute(f"UPDATE users SET Deck_1 = '{deck_1}' WHERE id_of_host = '{host_id}'")
                cur.execute(f"UPDATE users SET Deck_2 = '{deck_2}' WHERE id_of_host = '{host_id}'")
                conn.commit()
                cur.close()
                conn.close()

    elif callback.data == "p1_card_1" or callback.data == "p1_card_2" or callback.data == "p1_card_3" or callback.data == "p1_card_4" or callback.data == "p1_card_5" or callback.data == "p2_card_1" or callback.data == "p2_card_2" or callback.data == "p2_card_3" or callback.data == "p2_card_4" or callback.data == "p2_card_5":
        callback.data.split("_")
        I = int(callback.data.split("_")[2]) - 1
        deck_1 = ""
        deck_2 = ""
        p1_cards_mas = []
        p2_cards_mas = []

        host_id = None
        unhost_id = None
        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()
        for i in cur.execute(f"SELECT id_of_host FROM users WHERE id = '{callback.message.chat.id}'"):
            host_id = i[0]
        for i in cur.execute(f"SELECT id_of_unhost FROM users WHERE id = '{callback.message.chat.id}'"):
            unhost_id = i[0]
        conn.commit()
        cur.close()
        conn.close()

        conn = sqlite3.connect('orlock.sql')
        cur = conn.cursor()
        for i in cur.execute(f"SELECT Deck_1 FROM users WHERE id_of_host = '{host_id}'"):
            deck_1 = i[0]
        for i in cur.execute(f"SELECT Deck_2 FROM users WHERE id_of_host = '{host_id}'"):
            deck_2 = i[0]
        conn.commit()
        cur.close()
        conn.close()

        if (callback.data.split("_")[0] == "p1"):
            deck_1_mas = [0, 0, 0, 0, 0]
            deck_1_mas[0] = deck_1[0]
            deck_1_mas[1] = deck_1[1]
            deck_1_mas[2] = deck_1[2]
            deck_1_mas[3] = deck_1[3]
            deck_1_mas[4] = deck_1[4]
            a = deck_1_mas
            b = p1_cards_mas
            c = host_id
            d = "p1"
        if (callback.data.split("_")[0] == "p2"):
            deck_2_mas = [0, 0, 0, 0, 0]
            deck_2_mas[0] = deck_2[0]
            deck_2_mas[1] = deck_2[1]
            deck_2_mas[2] = deck_2[2]
            deck_2_mas[3] = deck_2[3]
            deck_2_mas[4] = deck_2[4]
            a = deck_2_mas
            b = p2_cards_mas
            c = unhost_id
            d = "p2"
        b.append(a[I])
        a.remove(a[I])
        deck_a = a[0] + a[1] + a[2] + a[3]
        for i in range(4):
            if (a[i] == "1"):
                a[i] = "⚔️"
            elif (a[i] == "2"):
                a[i] = "🛡️"
            elif (a[i] == "3"):
                a[i] = "🏹"
            elif (a[i] == "4"):
                a[i] = "🪖"
            elif (a[i] == "5"):
                a[i] = "⚡️"
        bot.delete_message(c, callback.message.message_id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton((a[0]), callback_data=d + "_card_1_2"))
        markup.add(types.InlineKeyboardButton((a[1]), callback_data=d + "_card_2_2"))
        markup.add(types.InlineKeyboardButton((a[2]), callback_data=d + "_card_3_2"))
        markup.add(types.InlineKeyboardButton((a[3]), callback_data=d + "_card_4_2"))
        bot.send_message(c, "Игра продолжается, выбери еще 1 карточку", reply_markup=markup)

        conn = sqlite3.connect('orlock.sql')
        cur = conn.cursor()

        if d == "p1" and len(a) == 4:
            cur.execute(f"UPDATE users SET P1_cards = '{b[0]}' WHERE id_of_host = '{host_id}'")
            cur.execute(f"UPDATE users SET Deck_1 = '{int(deck_a)}' WHERE id_of_host = '{host_id}'")
        elif d == "p2" and len(a) == 4:
            cur.execute(f"UPDATE users SET P2_cards = '{b[0]}' WHERE id_of_host = '{host_id}'")
            cur.execute(f"UPDATE users SET Deck_2 = '{int(deck_a)}' WHERE id_of_host = '{host_id}'")

        conn.commit()
        cur.close()
        conn.close()


    elif callback.data == "p1_card_1_2" or callback.data == "p1_card_2_2" or callback.data == "p1_card_3_2" or callback.data == "p1_card_4_2" or callback.data == "p2_card_1_2" or callback.data == "p2_card_2_2" or callback.data == "p2_card_3_2" or callback.data == "p2_card_4_2":
        callback.data.split("_")
        I = int(callback.data.split("_")[2]) - 1
        deck_1 = ""
        deck_2 = ""
        p1_cards = ""
        p2_cards = ""

        host_id = None
        unhost_id = None

        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()

        for i in cur.execute(f"SELECT id_of_host FROM users WHERE id = '{callback.message.chat.id}'"):
            host_id = i[0]
        for i in cur.execute(f"SELECT id_of_unhost FROM users WHERE id = '{callback.message.chat.id}'"):
            unhost_id = i[0]

        conn.commit()
        cur.close()
        conn.close()

        conn = sqlite3.connect('orlock.sql')
        cur = conn.cursor()

        for i in cur.execute(f"SELECT Deck_1 FROM users WHERE id_of_host = '{host_id}'"):
            deck_1 = i[0]
        for i in cur.execute(f"SELECT Deck_2 FROM users WHERE id_of_host = '{host_id}'"):
            deck_2 = i[0]
        for i in cur.execute(f"SELECT P1_cards FROM users WHERE id_of_host = '{host_id}'"):
            p1_cards = i[0]
        for i in cur.execute(f"SELECT P2_cards FROM users WHERE id_of_host = '{host_id}'"):
            p2_cards = i[0]

        conn.commit()
        cur.close()
        conn.close()

        if (callback.data.split("_")[0] == "p1"):
            deck_1_mas = [0] * 4
            deck_1_mas[0] = deck_1[0]
            deck_1_mas[1] = deck_1[1]
            deck_1_mas[2] = deck_1[2]
            deck_1_mas[3] = deck_1[3]
            a = deck_1_mas
            b = [p1_cards]
            c = host_id
            d = "P1"
        if (callback.data.split("_")[0] == "p2"):
            deck_2_mas = [0] * 4
            deck_2_mas[0] = deck_2[0]
            deck_2_mas[1] = deck_2[1]
            deck_2_mas[2] = deck_2[2]
            deck_2_mas[3] = deck_2[3]
            a = deck_2_mas
            b = [p2_cards]
            c = unhost_id
            d = "P2"
        b.append(a[I])
        a.remove(a[I])
        cards = b[0] + b[1]

        conn = sqlite3.connect('orlock.sql')
        cur = conn.cursor()

        if (d == "P1"):
            cur.execute(f"UPDATE users SET P1_cards = {cards} WHERE id_of_host = '{host_id}'")
            cards = None
        if (d == "P2"):
            cur.execute(f"UPDATE users SET P2_cards = {cards} WHERE id_of_host = '{host_id}'")
            cards = None

        conn.commit()
        cur.close()
        conn.close()
        bot.delete_message(c, callback.message.message_id)

        conn = sqlite3.connect('orlock.sql')
        cur = conn.cursor()

        p1_cards_mas = []
        p1_cards_str = ""
        for i in cur.execute(f"SELECT P1_cards FROM users WHERE id_of_host = '{host_id}'"):
            p1_cards_str = i[0]
        if p1_cards_str == None:
            p1_cards_str = "none"
        if len(p1_cards_str) == 2:
            p1_cards_mas.append(p1_cards_str[0])
            p1_cards_mas.append(p1_cards_str[1])

        p2_cards_mas = []
        p2_cards_str = ""
        for i in cur.execute(f"SELECT P2_cards FROM users WHERE id_of_host = '{host_id}'"):
            p2_cards_str = i[0]
        if p2_cards_str == None:
            p2_cards_str = "none"
        if len(p2_cards_str) == 2:
            p2_cards_mas.append(p2_cards_str[0])
            p2_cards_mas.append(p2_cards_str[1])

        conn.commit()
        cur.close()
        conn.close()

        if (len(p1_cards_mas) == 2 and len(p2_cards_mas) == 2):
            for i in range(2):
                if (p1_cards_mas[i] == "1"):
                    p1_cards_mas[i] = "⚔️"
                elif (p1_cards_mas[i] == "2"):
                    p1_cards_mas[i] = "🛡️"
                elif (p1_cards_mas[i] == "3"):
                    p1_cards_mas[i] = "🏹"
                elif (p1_cards_mas[i] == "4"):
                    p1_cards_mas[i] = "🪖"
                elif (p1_cards_mas[i] == "5"):
                    p1_cards_mas[i] = "⚡️"

            for i in range(2):
                if (p2_cards_mas[i] == "1"):
                    p2_cards_mas[i] = "⚔️"
                elif (p2_cards_mas[i] == "2"):
                    p2_cards_mas[i] = "🛡️"
                elif (p2_cards_mas[i] == "3"):
                    p2_cards_mas[i] = "🏹"
                elif (p2_cards_mas[i] == "4"):
                    p2_cards_mas[i] = "🪖"
                elif (p2_cards_mas[i] == "5"):
                    p2_cards_mas[i] = "⚡️"

            bot.send_message(host_id, f"Твоя колода: {p1_cards_mas[0]} {p1_cards_mas[1]}")
            bot.send_message(host_id, f"Колода противника: {p2_cards_mas[0]} {p2_cards_mas[1]}")
            bot.send_message(unhost_id, f"Твоя колода: {p2_cards_mas[0]} {p2_cards_mas[1]}")
            bot.send_message(unhost_id, f"Колода противника: {p1_cards_mas[0]} {p1_cards_mas[1]}")

            p1_sword = 0
            p1_bow = 0
            p1_shield = 0
            p1_helmet = 0
            p1_bonus = 0
            if (p1_cards_mas[0] == "⚔️"):
                p1_sword += 1
            if (p1_cards_mas[0] == "🛡️"):
                p1_shield += 1
            if (p1_cards_mas[0] == "🏹"):
                p1_bow += 1
            if (p1_cards_mas[0] == "🪖"):
                p1_helmet += 1
            if (p1_cards_mas[0] == "⚡️"):
                p1_bonus += 1
            if (p1_cards_mas[1] == "⚔️"):
                p1_sword += 1
            if (p1_cards_mas[1] == "🛡️"):
                p1_shield += 1
            if (p1_cards_mas[1] == "🏹"):
                p1_bow += 1
            if (p1_cards_mas[1] == "🪖"):
                p1_helmet += 1
            if (p1_cards_mas[1] == "⚡️"):
                p1_bonus += 1

            p2_sword = 0
            p2_bow = 0
            p2_shield = 0
            p2_helmet = 0
            p2_bonus = 0
            if (p2_cards_mas[0] == "⚔️"):
                p2_sword += 1
            if (p2_cards_mas[0] == "🛡️"):
                p2_shield += 1
            if (p2_cards_mas[0] == "🏹"):
                p2_bow += 1
            if (p2_cards_mas[0] == "🪖"):
                p2_helmet += 1
            if (p2_cards_mas[0] == "⚡️"):
                p2_bonus += 1
            if (p2_cards_mas[1] == "⚔️"):
                p2_sword += 1
            if (p2_cards_mas[1] == "🛡️"):
                p2_shield += 1
            if (p2_cards_mas[1] == "🏹"):
                p2_bow += 1
            if (p2_cards_mas[1] == "🪖"):
                p2_helmet += 1
            if (p2_cards_mas[1] == "⚡️"):
                p2_bonus += 1

            p1_health = 3
            p2_health = 3

            if (p1_helmet - p2_sword < 0):
                p1_health += p1_helmet - p2_sword
            if (p2_helmet - p1_sword < 0):
                p2_health += p2_helmet - p1_sword
            if (p1_shield - p2_bow < 0):
                p1_health += p1_shield - p2_bow
            if (p2_shield - p1_bow < 0):
                p2_health += p2_shield - p1_bow
            bot.send_message(host_id, f"Твое здоровье: {'❤️' * p1_health}")
            bot.send_message(unhost_id, f"Твое здоровье: {'❤️' * p2_health}")

            conn = sqlite3.connect('orlock.sql')
            cur = conn.cursor()
# начинаются работы над энергией
            if p1_bonus > 0:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Заклинание Ярость", callback_data = "p1_damage" ))
                markup.add(types.InlineKeyboardButton("Заклинание Мудрость", callback_data = "p1_heal"))
                bot.send_message(host_id, f"У тебя есть энегрия: {p1_bonus}! Выбери чары:", reply_markup=markup)
                cur.execute(f"UPDATE users SET P1_cards = {0} WHERE id_of_host = '{host_id}'")
                cur.execute(f"UPDATE users SET Deck_1 = {0} WHERE id_of_host = '{host_id}'")
                cur.execute(f"UPDATE users SET P1_health = {p1_health} WHERE id_of_host = '{host_id}'")
                cur.execute(f"UPDATE users SET P1_bonus = {p1_bonus} WHERE id_of_host = '{host_id}'")
            if p2_bonus > 0:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Заклинание Ярость", callback_data = "p2_damage" ))
                markup.add(types.InlineKeyboardButton("Заклинание Мудрость", callback_data = "p2_heal"))
                bot.send_message(unhost_id, f"У тебя есть энегрия: {p2_bonus}! Выбери чары:", reply_markup=markup)
                cur.execute(f"UPDATE users SET P2_cards = {0} WHERE id_of_host = '{host_id}'")
                cur.execute(f"UPDATE users SET Deck_2 = {0} WHERE id_of_host = '{host_id}'")
                cur.execute(f"UPDATE users SET P2_health = {p2_health} WHERE id_of_host = '{host_id}'")
                cur.execute(f"UPDATE users SET P2_bonus = {p2_bonus} WHERE id_of_host = '{host_id}'")

            conn.commit()
            cur.close()
            conn.close()
            if p1_bonus == 0:
                conn = sqlite3.connect('orlock.sql')
                cur = conn.cursor()
                cur.execute(f"UPDATE users SET P1_cards = {0} WHERE id_of_host = '{host_id}'")
                cur.execute(f"UPDATE users SET Deck_1 = {0} WHERE id_of_host = '{host_id}'")
                cur.execute(f"UPDATE users SET P1_health = {p1_health} WHERE id_of_host = '{host_id}'")
                conn.commit()
                cur.close()
                conn.close()
            if p2_bonus == 0:
                ready = 0
                conn = sqlite3.connect('orlock.sql')
                cur = conn.cursor()
                cur.execute(f"UPDATE users SET P2_cards = {0} WHERE id_of_host = '{host_id}'")
                cur.execute(f"UPDATE users SET Deck_2 = {0} WHERE id_of_host = '{host_id}'")
                cur.execute(f"UPDATE users SET P2_health = {p2_health} WHERE id_of_host = '{host_id}'")
                conn.commit()
                cur.close()
                conn.close()
            if p1_bonus == 0 and p2_bonus == 0:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Продолжить", callback_data="continue"))
                bot.send_message(host_id, "Нажми на кнопку!", reply_markup=markup)

    elif callback.data == "p1_damage" or callback.data == "p2_damage" or callback.data == "p1_heal" or callback.data == "p2_heal":
        host_id = None
        unhost_id = None
        p1_bonus = 0
        p2_bonus = 0

        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()
        for i in cur.execute(f"SELECT id_of_host FROM users WHERE id = '{callback.message.chat.id}'"):
            host_id = i[0]
        for i in cur.execute(f"SELECT id_of_unhost FROM users WHERE id = '{callback.message.chat.id}'"):
            unhost_id = i[0]
        conn.commit()
        cur.close()
        conn.close()

        conn = sqlite3.connect('orlock.sql')
        cur = conn.cursor()
        for i in cur.execute(f"SELECT P1_bonus FROM users WHERE id_of_host = '{host_id}'"):
            p1_bonus = i[0]
        for i in cur.execute(f"SELECT P2_bonus FROM users WHERE id_of_host = '{host_id}'"):
            p2_bonus = i[0]
        conn.commit()
        cur.close()
        conn.close()

        host_result = 0
        unhost_result = 0

        if callback.data == "p1_damage" or callback.data == "p1_heal":
            bot.delete_message(host_id, callback.message.message_id)
            send_football_1 = bot.send_dice(host_id, "⚽")
            host_result = send_football_1.dice.value
            time.sleep(5)

        if callback.data == "p2_damage" or callback.data == "p2_heal":
            bot.delete_message(unhost_id, callback.message.message_id)
            send_football_2 = bot.send_dice(unhost_id, "⚽")
            unhost_result = send_football_2.dice.value
            time.sleep(5)

        if (callback.data.split("_")[0] == "p1" and callback.data.split("_")[1] == "damage" and host_result > 3):
            damage = 0
            health_of_opponent = 0

            conn = sqlite3.connect('orlock.sql')
            cur = conn.cursor()
            for i in cur.execute(f"SELECT P1_bonus FROM users WHERE id_of_host = '{host_id}'"):
                damage = i[0]
            for i in cur.execute(f"SELECT P2_health FROM users WHERE id_of_host = '{host_id}'"):
                health_of_opponent = i[0]
            conn.commit()
            cur.close()
            conn.close()

            health_of_opponent = health_of_opponent - int(damage)
            bot.send_message(unhost_id, f"Твое здоровье: {'❤️' * health_of_opponent}")

            conn = sqlite3.connect('orlock.sql')
            cur = conn.cursor()
            cur.execute(f"UPDATE users SET P2_health = {health_of_opponent} WHERE id_of_host = '{host_id}'")
            cur.execute(f"UPDATE users SET P1_bonus = {0} WHERE id_of_host = '{host_id}'")
            conn.commit()
            cur.close()
            conn.close()

        elif host_result >= 0 and host_result < 3 and callback.data.split("_")[0] == "p1" and callback.data.split("_")[1] == "damage":
            conn = sqlite3.connect('orlock.sql')
            cur = conn.cursor()
            cur.execute(f"UPDATE users SET P1_bonus = {0} WHERE id_of_host = '{host_id}'")
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(host_id, "Твоя энергия сгорела!")

        if (callback.data.split("_")[0] == "p2" and callback.data.split("_")[1] == "damage" and unhost_result >= 3):
            damage = 0
            health_of_opponent = 0

            conn = sqlite3.connect('orlock.sql')
            cur = conn.cursor()
            for i in cur.execute(f"SELECT P2_bonus FROM users WHERE id_of_host = '{host_id}'"):
                damage = i[0]
            for i in cur.execute(f"SELECT P1_health FROM users WHERE id_of_host = '{host_id}'"):
                health_of_opponent = i[0]
            conn.commit()
            cur.close()
            conn.close()

            health_of_opponent = int(health_of_opponent) - damage
            bot.send_message(host_id, f"Твое здоровье: {'❤️' * health_of_opponent}")

            conn = sqlite3.connect('orlock.sql')
            cur = conn.cursor()
            cur.execute(f"UPDATE users SET P1_health = {health_of_opponent} WHERE id_of_host = '{host_id}'")
            cur.execute(f"UPDATE users SET P2_bonus = {0} WHERE id_of_host = '{host_id}'")
            conn.commit()
            cur.close()
            conn.close()

        elif unhost_result >= 0 and unhost_result < 3 and callback.data.split("_")[0] == "p2" and callback.data.split("_")[1] == "damage":
            conn = sqlite3.connect('orlock.sql')
            cur = conn.cursor()
            cur.execute(f"UPDATE users SET P2_bonus = {0} WHERE id_of_host = '{host_id}'")
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(unhost_id, "Твоя энергия сгорела!")

        if (callback.data.split("_")[0] == "p1" and callback.data.split("_")[1] == "heal" and host_result >= 3):
            health = 0
            heal = 0

            conn = sqlite3.connect('orlock.sql')
            cur = conn.cursor()
            for i in cur.execute(f"SELECT P1_bonus FROM users WHERE id_of_host = '{host_id}'"):
                heal = i[0]
            for i in cur.execute(f"SELECT P1_health FROM users WHERE id_of_host = '{host_id}'"):
                health = i[0]
            conn.commit()
            cur.close()
            conn.close()

            health = health + heal

            conn = sqlite3.connect('orlock.sql')
            cur = conn.cursor()
            cur.execute(f"UPDATE users SET P1_health = {health} WHERE id_of_host = '{host_id}'")
            cur.execute(f"UPDATE users SET P1_bonus = {0} WHERE id_of_host = '{host_id}'")
            conn.commit()
            cur.close()
            conn.close()

            bot.send_message(host_id, f"Твое здоровье: {'❤️' * health}")
        elif host_result >= 0 and host_result < 3 and callback.data.split("_")[0] == "p1" and callback.data.split("_")[1] == "heal":
            conn = sqlite3.connect('orlock.sql')
            cur = conn.cursor()
            cur.execute(f"UPDATE users SET P1_bonus = {0} WHERE id_of_host = '{host_id}'")
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(host_id, "Твоя энергия сгорела!")

        if (callback.data.split("_")[0] == "p2" and callback.data.split("_")[1] == "heal" and unhost_result >= 3):
            health = 0
            heal = 0

            conn = sqlite3.connect('orlock.sql')
            cur = conn.cursor()
            for i in cur.execute(f"SELECT P2_bonus FROM users WHERE id_of_host = '{host_id}'"):
                heal = i[0]
            for i in cur.execute(f"SELECT P2_health FROM users WHERE id_of_host = '{host_id}'"):
                health = i[0]
            conn.commit()
            cur.close()
            conn.close()

            health = health + heal

            conn = sqlite3.connect('orlock.sql')
            cur = conn.cursor()
            cur.execute(f"UPDATE users SET P2_health = {health} WHERE id_of_host = '{host_id}'")
            cur.execute(f"UPDATE users SET P2_bonus = {0} WHERE id_of_host = '{host_id}'")
            conn.commit()
            cur.close()
            conn.close()

            bot.send_message(unhost_id, f"Твое здоровье: {'❤️' * health}")
        elif unhost_result >= 0 and unhost_result < 3 and callback.data.split("_")[0] == "p2" and callback.data.split("_")[1] == "heal":
            conn = sqlite3.connect('orlock.sql')
            cur = conn.cursor()
            cur.execute(f"UPDATE users SET P2_bonus = {0} WHERE id_of_host = '{host_id}'")
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(unhost_id, "Твоя энергия сгорела!")

        readiness = 0
        conn = sqlite3.connect('orlock.sql')
        cur = conn.cursor()
        for i in cur.execute(f"SELECT Continue FROM users WHERE id_of_host = '{host_id}'"):
            readiness = i[0]
        cur.execute(f"UPDATE users SET Continue = {readiness + 1} WHERE id_of_host = '{host_id}'")
        for i in cur.execute(f"SELECT Continue FROM users WHERE id_of_host = '{host_id}'"):
            readiness = i[0]
        conn.commit()
        cur.close()
        conn.close()

        if readiness == 1:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Продолжить", callback_data="continue"))
            bot.send_message(host_id, "Нажми на кнопку!", reply_markup=markup)


# работы закончены

    elif callback.data == "continue":
        host_id = None
        unhost_id = None

        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()
        for i in cur.execute(f"SELECT id_of_host FROM users WHERE id = '{callback.message.chat.id}'"):
            host_id = i[0]
        for i in cur.execute(f"SELECT id_of_unhost FROM users WHERE id = '{callback.message.chat.id}'"):
            unhost_id = i[0]
        conn.commit()
        cur.close()
        conn.close()

        bot.delete_message(host_id, callback.message.message_id)

        deck_1_mas = []
        deck_1 = ""
        for i in range(3):
            a = random.randint(1, 4) # изменены границы
            deck_1 += str(a)
            if (a == 1):
                deck_1_mas.append("⚔️")
            if (a == 2):
                deck_1_mas.append("🛡️")
            if (a == 3):
                deck_1_mas.append("🏹")
            if (a == 4):
                deck_1_mas.append("🪖")
            if (a == 5):
                deck_1_mas.append("⚡️")

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton((deck_1_mas[0]), callback_data="r2_p1_card_1"))
        markup.add(types.InlineKeyboardButton((deck_1_mas[1]), callback_data="r2_p1_card_2"))
        markup.add(types.InlineKeyboardButton((deck_1_mas[2]), callback_data="r2_p1_card_3"))
        bot.send_message(host_id, "Игра началась, выбери 2 карточки", reply_markup=markup)

        deck_2_mas = []
        deck_2 = ""
        for i in range(3):
            a = random.randint(1, 4) # изменены границы
            deck_2 += str(a)
            if (a == 1):
                deck_2_mas.append("⚔️")
            if (a == 2):
                deck_2_mas.append("🛡️")
            if (a == 3):
                deck_2_mas.append("🏹")
            if (a == 4):
                deck_2_mas.append("🪖")
            if (a == 5):
                deck_2_mas.append("⚡️")

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton((deck_2_mas[0]), callback_data="r2_p2_card_1"))
        markup.add(types.InlineKeyboardButton((deck_2_mas[1]), callback_data="r2_p2_card_2"))
        markup.add(types.InlineKeyboardButton((deck_2_mas[2]), callback_data="r2_p2_card_3"))
        bot.send_message(unhost_id, "Игра началась, выбери 2 карточки", reply_markup=markup)
        bot.send_message(unhost_id,f"Карты на выбор противника: {deck_1_mas[0]} {deck_1_mas[1]} {deck_1_mas[2]}")
        bot.send_message(host_id,f"Карты на выбор противника: {deck_2_mas[0]} {deck_2_mas[1]} {deck_2_mas[2]}")

        conn = sqlite3.connect('orlock.sql')
        cur = conn.cursor()
        cur.execute(f"UPDATE users SET Deck_1 = '{deck_1}' WHERE id_of_host = '{host_id}'")
        cur.execute(f"UPDATE users SET Deck_2 = '{deck_2}' WHERE id_of_host = '{host_id}'")
        conn.commit()
        cur.close()
        conn.close()

    elif callback.data == "r2_p1_card_1" or callback.data == "r2_p1_card_2" or callback.data == "r2_p1_card_3" or callback.data == "r2_p2_card_1" or callback.data == "r2_p2_card_2" or callback.data == "r2_p2_card_3":
        callback.data.split("_")
        I = int(callback.data.split("_")[3]) - 1
        deck_1 = ""
        deck_2 = ""
        p1_cards_mas = []
        p2_cards_mas = []

        host_id = None
        unhost_id = None
        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()
        for i in cur.execute(f"SELECT id_of_host FROM users WHERE id = '{callback.message.chat.id}'"):
            host_id = i[0]
        for i in cur.execute(f"SELECT id_of_unhost FROM users WHERE id = '{callback.message.chat.id}'"):
            unhost_id = i[0]
        conn.commit()
        cur.close()
        conn.close()

        conn = sqlite3.connect('orlock.sql')
        cur = conn.cursor()
        for i in cur.execute(f"SELECT Deck_1 FROM users WHERE id_of_host = '{host_id}'"):
            deck_1 = i[0]
        for i in cur.execute(f"SELECT Deck_2 FROM users WHERE id_of_host = '{host_id}'"):
            deck_2 = i[0]
        conn.commit()
        cur.close()
        conn.close()

        if (callback.data.split("_")[1] == "p1"):
            deck_1_mas = [0, 0, 0]
            deck_1_mas[0] = deck_1[0]
            deck_1_mas[1] = deck_1[1]
            deck_1_mas[2] = deck_1[2]
            a = deck_1_mas
            b = p1_cards_mas
            c = host_id
            d = "r2_p1"
        if (callback.data.split("_")[1] == "p2"):
            deck_2_mas = [0, 0, 0]
            deck_2_mas[0] = deck_2[0]
            deck_2_mas[1] = deck_2[1]
            deck_2_mas[2] = deck_2[2]
            a = deck_2_mas
            b = p2_cards_mas
            c = unhost_id
            d = "r2_p2"
        b.append(a[I])
        a.remove(a[I])
        deck_a = a[0] + a[1]
        for i in range(2):
            if (a[i] == "1"):
                a[i] = "⚔️"
            elif (a[i] == "2"):
                a[i] = "🛡️"
            elif (a[i] == "3"):
                a[i] = "🏹"
            elif (a[i] == "4"):
                a[i] = "🪖"
            elif (a[i] == "5"):
                a[i] = "⚡️"
        bot.delete_message(c, callback.message.message_id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton((a[0]), callback_data=d + "_card_1_2"))
        markup.add(types.InlineKeyboardButton((a[1]), callback_data=d + "_card_2_2"))
        bot.send_message(c, "Игра продолжается, выбери еще 1 карточку", reply_markup=markup)

        conn = sqlite3.connect('orlock.sql')
        cur = conn.cursor()

        if d == "r2_p1" and len(a) == 2:
            cur.execute(f"UPDATE users SET P1_cards = '{b[0]}' WHERE id_of_host = '{host_id}'")
            cur.execute(f"UPDATE users SET Deck_1 = '{int(deck_a)}' WHERE id_of_host = '{host_id}'")
        elif d == "r2_p2" and len(a) == 2:
            cur.execute(f"UPDATE users SET P2_cards = '{b[0]}' WHERE id_of_host = '{host_id}'")
            cur.execute(f"UPDATE users SET Deck_2 = '{int(deck_a)}' WHERE id_of_host = '{host_id}'")

        conn.commit()
        cur.close()
        conn.close()
    elif callback.data == "r2_p1_card_1_2" or callback.data == "r2_p1_card_2_2" or callback.data == "r2_p2_card_1_2" or callback.data == "r2_p2_card_2_2":
        callback.data.split("_")
        I = int(callback.data.split("_")[3]) - 1
        deck_1 = ""
        deck_2 = ""
        p1_cards = ""
        p2_cards = ""

        host_id = None
        unhost_id = None

        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()

        for i in cur.execute(f"SELECT id_of_host FROM users WHERE id = '{callback.message.chat.id}'"):
            host_id = i[0]
        for i in cur.execute(f"SELECT id_of_unhost FROM users WHERE id = '{callback.message.chat.id}'"):
            unhost_id = i[0]

        conn.commit()
        cur.close()
        conn.close()

        conn = sqlite3.connect('orlock.sql')
        cur = conn.cursor()

        for i in cur.execute(f"SELECT Deck_1 FROM users WHERE id_of_host = '{host_id}'"):
            deck_1 = i[0]
        for i in cur.execute(f"SELECT Deck_2 FROM users WHERE id_of_host = '{host_id}'"):
            deck_2 = i[0]
        for i in cur.execute(f"SELECT P1_cards FROM users WHERE id_of_host = '{host_id}'"):
            p1_cards = i[0]
        for i in cur.execute(f"SELECT P2_cards FROM users WHERE id_of_host = '{host_id}'"):
            p2_cards = i[0]

        conn.commit()
        cur.close()
        conn.close()

        if (callback.data.split("_")[1] == "p1"):
            deck_1_mas = [0] * 4
            deck_1_mas[0] = deck_1[0]
            deck_1_mas[1] = deck_1[1]
            a = deck_1_mas
            b = [p1_cards]
            c = host_id
            d = "p1"
        if (callback.data.split("_")[1] == "p2"):
            deck_2_mas = [0] * 4
            deck_2_mas[0] = deck_2[0]
            deck_2_mas[1] = deck_2[1]
            a = deck_2_mas
            b = [p2_cards]
            c = unhost_id
            d = "p2"
        b.append(a[I])
        a.remove(a[I])
        cards = b[0] + b[1]

        conn = sqlite3.connect('orlock.sql')
        cur = conn.cursor()

        if (d == "p1"):
            cur.execute(f"UPDATE users SET P1_cards = {cards} WHERE id_of_host = '{host_id}'")
            cards = None
        if (d == "p2"):
            cur.execute(f"UPDATE users SET P2_cards = {cards} WHERE id_of_host = '{host_id}'")
            cards = None

        conn.commit()
        cur.close()
        conn.close()
        bot.delete_message(c, callback.message.message_id)

        conn = sqlite3.connect('orlock.sql')
        cur = conn.cursor()

        p1_cards_mas = []
        p1_cards_str = ""
        for i in cur.execute(f"SELECT P1_cards FROM users WHERE id_of_host = '{host_id}'"):
            p1_cards_str = i[0]
        if p1_cards_str == None:
            p1_cards_str = "none"
        if len(p1_cards_str) == 2:
            p1_cards_mas.append(p1_cards_str[0])
            p1_cards_mas.append(p1_cards_str[1])

        p2_cards_mas = []
        p2_cards_str = ""
        for i in cur.execute(f"SELECT P2_cards FROM users WHERE id_of_host = '{host_id}'"):
            p2_cards_str = i[0]
        if p2_cards_str == None:
            p2_cards_str = "none"
        if len(p2_cards_str) == 2:
            p2_cards_mas.append(p2_cards_str[0])
            p2_cards_mas.append(p2_cards_str[1])

        conn.commit()
        cur.close()
        conn.close()

        if (len(p1_cards_mas) == 2 and len(p2_cards_mas) == 2):
            for i in range(2):
                if (p1_cards_mas[i] == "1"):
                    p1_cards_mas[i] = "⚔️"
                elif (p1_cards_mas[i] == "2"):
                    p1_cards_mas[i] = "🛡️"
                elif (p1_cards_mas[i] == "3"):
                    p1_cards_mas[i] = "🏹"
                elif (p1_cards_mas[i] == "4"):
                    p1_cards_mas[i] = "🪖"
                elif (p1_cards_mas[i] == "5"):
                    p1_cards_mas[i] = "⚡️"

            for i in range(2):
                if (p2_cards_mas[i] == "1"):
                    p2_cards_mas[i] = "⚔️"
                elif (p2_cards_mas[i] == "2"):
                    p2_cards_mas[i] = "🛡️"
                elif (p2_cards_mas[i] == "3"):
                    p2_cards_mas[i] = "🏹"
                elif (p2_cards_mas[i] == "4"):
                    p2_cards_mas[i] = "🪖"
                elif (p2_cards_mas[i] == "5"):
                    p2_cards_mas[i] = "⚡️"

            bot.send_message(host_id, f"Твоя колода: {p1_cards_mas[0]} {p1_cards_mas[1]}")
            bot.send_message(host_id, f"Колода противника: {p2_cards_mas[0]} {p2_cards_mas[1]}")
            bot.send_message(unhost_id, f"Твоя колода: {p2_cards_mas[0]} {p2_cards_mas[1]}")
            bot.send_message(unhost_id, f"Колода противника: {p1_cards_mas[0]} {p1_cards_mas[1]}")

            p1_sword = 0
            p1_bow = 0
            p1_shield = 0
            p1_helmet = 0
            p1_bonus = 0
            if (p1_cards_mas[0] == "⚔️"):
                p1_sword += 1
            if (p1_cards_mas[0] == "🛡️"):
                p1_shield += 1
            if (p1_cards_mas[0] == "🏹"):
                p1_bow += 1
            if (p1_cards_mas[0] == "🪖"):
                p1_helmet += 1
            if (p1_cards_mas[0] == "⚡️"):
                p1_bonus += 1
            if (p1_cards_mas[1] == "⚔️"):
                p1_sword += 1
            if (p1_cards_mas[1] == "🛡️"):
                p1_shield += 1
            if (p1_cards_mas[1] == "🏹"):
                p1_bow += 1
            if (p1_cards_mas[1] == "🪖"):
                p1_helmet += 1
            if (p1_cards_mas[1] == "⚡️"):
                p1_bonus += 1

            p2_sword = 0
            p2_bow = 0
            p2_shield = 0
            p2_helmet = 0
            p2_bonus = 0
            if (p2_cards_mas[0] == "⚔️"):
                p2_sword += 1
            if (p2_cards_mas[0] == "🛡️"):
                p2_shield += 1
            if (p2_cards_mas[0] == "🏹"):
                p2_bow += 1
            if (p2_cards_mas[0] == "🪖"):
                p2_helmet += 1
            if (p2_cards_mas[0] == "⚡️"):
                p2_bonus += 1
            if (p2_cards_mas[1] == "⚔️"):
                p2_sword += 1
            if (p2_cards_mas[1] == "🛡️"):
                p2_shield += 1
            if (p2_cards_mas[1] == "🏹"):
                p2_bow += 1
            if (p2_cards_mas[1] == "🪖"):
                p2_helmet += 1
            if (p2_cards_mas[1] == "⚡️"):
                p2_bonus += 1

            p1_health = None
            p2_health = None

            conn = sqlite3.connect('orlock.sql')
            cur = conn.cursor()
            for i in cur.execute(f"SELECT P1_health FROM users WHERE id_of_host = '{host_id}'"):
                p1_health = i[0]
            for i in cur.execute(f"SELECT P2_health FROM users WHERE id_of_host = '{host_id}'"):
                p2_health = i[0]
            conn.commit()
            cur.close()
            conn.close()

            if (p1_helmet - p2_sword < 0):
                p1_health += p1_helmet - p2_sword
            if (p2_helmet - p1_sword < 0):
                p2_health += p2_helmet - p1_sword
            if (p1_shield - p2_bow < 0):
                p1_health += p1_shield - p2_bow
            if (p2_shield - p1_bow < 0):
                p2_health += p2_shield - p1_bow


            if (p1_health > 0 and p2_health <= 0) or (p1_health > p2_health):
                player_1 = 1
                player_2 = 0
                bot.send_message(host_id, f"Твое здоровье: {'❤️' * p1_health}")

                conn = sqlite3.connect('orlock.sql')
                cur = conn.cursor()
                cur.execute(f"DELETE FROM users WHERE id_of_host = {host_id}")
                conn.commit()
                cur.close()
                conn.close()

                conn = sqlite3.connect('data.sql')
                cur = conn.cursor()
                cur.execute(f"UPDATE users SET id_of_host = {0} WHERE id = {host_id}")
                cur.execute(f"UPDATE users SET id_of_unhost = {0} WHERE id = {host_id}")
                cur.execute(f"UPDATE users SET id_of_host = {0} WHERE id = {unhost_id}")
                cur.execute(f"UPDATE users SET id_of_unhost = {0} WHERE id = {unhost_id}")
                conn.commit()
                cur.close()
                conn.close()

            if (p2_health > 0 and p1_health <= 0) or (p2_health > p1_health):
                player_1 = 0
                player_2 = 1
                bot.send_message(unhost_id, f"Твое здоровье: {'❤️' * p2_health}")

                conn = sqlite3.connect('orlock.sql')
                cur = conn.cursor()
                cur.execute(f"DELETE FROM users WHERE id_of_host = {host_id}")
                conn.commit()
                cur.close()
                conn.close()

                conn = sqlite3.connect('data.sql')
                cur = conn.cursor()
                cur.execute(f"UPDATE users SET id_of_host = {0} WHERE id = {host_id}")
                cur.execute(f"UPDATE users SET id_of_unhost = {0} WHERE id = {host_id}")
                cur.execute(f"UPDATE users SET id_of_host = {0} WHERE id = {unhost_id}")
                cur.execute(f"UPDATE users SET id_of_unhost = {0} WHERE id = {unhost_id}")
                conn.commit()
                cur.close()
                conn.close()

            if (p2_health <= 0 and p1_health <= 0) or (p2_health == p1_health):
                player_1 = 1
                player_2 = 1

                conn = sqlite3.connect('orlock.sql')
                cur = conn.cursor()
                cur.execute(f"DELETE FROM users WHERE id_of_host = {host_id}")
                conn.commit()
                cur.close()
                conn.close()

                conn = sqlite3.connect('data.sql')
                cur = conn.cursor()
                cur.execute(f"UPDATE users SET id_of_host = {0} WHERE id = {host_id}")
                cur.execute(f"UPDATE users SET id_of_unhost = {0} WHERE id = {host_id}")
                cur.execute(f"UPDATE users SET id_of_host = {0} WHERE id = {unhost_id}")
                cur.execute(f"UPDATE users SET id_of_unhost = {0} WHERE id = {unhost_id}")
                conn.commit()
                cur.close()
                conn.close()

            conn = sqlite3.connect('data.sql')
            cur = conn.cursor()
            for i in cur.execute(f"SELECT coins FROM users WHERE id = {host_id}"):
                balance_1 = i[0]
            for i in cur.execute(f"SELECT coins FROM users WHERE id = {unhost_id}"):
                balance_2 = i[0]
            if player_1 == player_2:
                bot.send_message(host_id, f"Ничья, в твоем распоряжении {balance_1} Coins 🟡")
                bot.send_message(unhost_id, f"Ничья, в твоем распоряжении {balance_2} Coins 🟡")
            elif player_1 > player_2:
                bot.send_message(host_id, f"Победа, в твоем распоряжении {balance_1 + 100} Coins 🟡")
                bot.send_message(unhost_id, f"Поражение, в твоем распоряжении {balance_2 - 100} Coins 🟡")
                cur.execute(f"UPDATE users SET coins = {balance_1 + 100} WHERE id = {host_id}")
                cur.execute(f"UPDATE users SET coins = {balance_2 - 100} WHERE id = {unhost_id}")
            else:
                bot.send_message(host_id, f"Поражение, в твоем распоряжении {balance_1 - 100} Coins 🟡")
                bot.send_message(unhost_id, f"Победа, в твоем распоряжении {balance_2 + 100} Coins 🟡")
                cur.execute(f"UPDATE users SET coins = {balance_2 + 100} WHERE id = {unhost_id}")
                cur.execute(f"UPDATE users SET coins = {balance_1 - 100} WHERE id = {host_id}")
            cur.execute(f"UPDATE users SET in_game = 0 WHERE id = '{host_id}'")
            cur.execute(f"UPDATE users SET in_game = 0 WHERE id = '{unhost_id}'")
            conn.commit()
            cur.close()
            conn.close()


bot.polling(none_stop=True)
