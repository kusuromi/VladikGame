import pygame
import sys
import textwrap
import random
import os
import time

# --- Инициализация Pygame ---
pygame.init()

# --- Константы ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
BG_COLOR = (23, 37, 84) 
TEXT_COLOR = (203, 213, 225) 
ACCENT_COLOR = (251, 191, 36) 
CHOICE_BG_COLOR = (30, 41, 59)
CHOICE_HOVER_COLOR = (51, 65, 85)
RED = (220, 38, 38)
GREEN = (34, 197, 94)
YELLOW = (234, 179, 8)

# --- Настройка окна ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Эхо Забвения")


# --- Шрифты (ИСПРАВЛЕНО) ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

FONT_PATH = resource_path('MorrisRoman-Black.ttf')

# Попытка загрузить красивый шрифт, иначе берем системный
try:
    NARRATIVE_FONT = pygame.font.Font(FONT_PATH, 28)
    HEADER_FONT = pygame.font.Font(FONT_PATH, 48)
except (pygame.error, FileNotFoundError):
    print("Внимание: Кастомный шрифт не найден. Используется системный.")
    NARRATIVE_FONT = pygame.font.SysFont("arial", 28)
    HEADER_FONT = pygame.font.SysFont("arial", 48, bold=True)

# UI шрифт всегда лучше брать системный или читаемый
UI_FONT = pygame.font.SysFont("arial", 22)
CHOICE_FONT = pygame.font.SysFont("arial", 18)


# --- Словарь с сюжетом (Оставлен без изменений) ---
STORY = {
    'start': {
        'location': "Тюремная камера",
        'narrative': "Вы медленно приходите в себя на холодном каменном полу. Голова гудит, а в нос ударяет запах сырости и отчаяния. Вы находитесь в тускло освещенной камере.",
        'choices': [
            {'text': "Осмотреться в камере", 'nextId': "look_around_cell"},
            {'text': "Подойти к решетке и осмотреть замок", 'nextId': "check_lock"},
        ],
    },
    'look_around_cell': {
        'location': "Тюремная камера",
        'narrative': "Вы обшариваете каждый угол камеры. В одном из них — куча гнилой соломы, а в стене напротив решетки вы замечаете камень, который, кажется, немного выпирает из кладки.",
        'choices': [
            {'text': "Исследовать выпирающий камень", 'nextId': "pry_stone"},
            {'text': "Покопаться в гнилой соломе", 'nextId': "check_straw"},
        ],
    },
    'pry_stone': {
        'location': "Тюремная камера",
        'narrative': "С трудом выковыриваете камень из стены. За ним оказывается ниша, в которой лежит старый, покрытый ржавчиной ключ.",
        'narrativeAfterGained': "Вы снова осматриваете нишу за камнем, но она пуста.",
        'itemGained': {'name': "ржавый ключ", 'description': "Маленький, ржавый ключ.", 'quantity': 1},
        'choices': [
            {'text': "Попробовать ключ на замке решетки", 'nextId': "unlock_door", 'requiredItem': "ржавый ключ"},
            {'text': "Продолжить осматривать камеру", 'nextId': "look_around_cell_again"},
        ],
    },
    'check_lock': {
        'location': "Тюремная камера",
        'narrative': "Вы подходите к решетке. Массивный замок висит на двери, он выглядит старым, но все еще очень прочным.",
        'choices': [
            {'text': "Осмотреться в камере", 'nextId': "look_around_cell"},
            {'text': "Открыть замок ржавым ключом", 'nextId': "unlock_door", 'requiredItem': "ржавый ключ"},
        ],
    },
     'check_straw': {
        'location': "Тюремная камера",
        'narrative': "Вы ворошите гнилую солому. Ничего полезного вы не находите.",
        'choices': [
            {'text': "Исследовать выпирающий камень", 'nextId': "pry_stone"},
        ],
    },
    'look_around_cell_again': {
        'location': "Тюремная камера",
        'narrative': "Вы уже все осмотрели. Больше здесь ничего нет.",
        'choices': [
            {'text': "Попробовать ключ на замке решетки", 'nextId': "unlock_door", 'requiredItem': "ржавый ключ"},
        ],
    },
    'unlock_door': {
        'location': "Тюремная камера",
        'narrative': "Вы вставляете ржавый ключ в замок. Раздается громкий щелчок, и замок открывается. Путь на свободу открыт!",
        'itemLost': "ржавый ключ",
        'choices': [
            {'text': "Выйти в коридор", 'nextId': "corridor_entrance"},
        ],
    },
    'corridor_entrance': {
        'location': "Коридор",
        'narrative': "Вы выходите в длинный, темный коридор. В одном конце слышны голоса, в другом — тишина.",
        'choices': [
            {'text': "Пойти направо, в сторону голосов", 'nextId': "corridor_guards"},
            {'text': "Пойти налево, в темноту", 'nextId': "corridor_darkness"},
        ],
    },
    'corridor_guards': {
        'location': "Коридор",
        'narrative': "Вы крадетесь в сторону голосов и видите двух стражников. Пройти мимо них незамеченным кажется невозможным.",
        'choices': [
            {'text': "Напасть на стражников", 'nextId': "attack_fail_game_over"},
            {'text': "Вернуться и пойти в другую сторону", 'nextId': "corridor_darkness"},
        ]
    },
    'attack_fail_game_over': {
        'location': "Пост охраны",
        'narrative': "Вы бросаетесь на двух вооруженных стражников. Это был смелый, но глупый поступок.",
        'choices': [],
        'gameOver': {'isOver': True, 'message': "Вы погибли в неравном бою."}
    },
    'corridor_darkness': {
        'location': "Темный коридор",
        'narrative': "Вы идете в тишине и видите перед собой ветхую деревянную дверь.",
        'choices': [
            {'text': "Открыть дверь", 'nextId': "storage_room"},
        ],
    },
    'storage_room': {
        'location': "Кладовая",
        'narrative': "Вы попадаете в пыльную кладовую. В углу стоят несколько бочек, а на стене висит старый плащ.",
        'choices': [
            {'text': "Взять плащ", 'nextId': "take_cloak", 'forbiddenItem': "старый плащ"},
            {'text': "Осмотреть бочки", 'nextId': "check_barrels"},
            {'text': "Выйти в коридор", 'nextId': "corridor_darkness_return"}
        ]
    },
    'take_cloak': {
        'location': "Кладовая",
        'narrative': "Вы снимаете с крюка тяжелый, пыльный плащ.",
        'narrativeAfterGained': "Крюк на стене пуст.",
        'itemGained': {'name': "старый плащ", 'description': "Плотный плащ.", 'quantity': 1, 'slot': 'torso', 'defenseBonus': 5},
        'choices': [
            {'text': "Осмотреть бочки", 'nextId': "check_barrels"},
            {'text': "Выйти в коридор", 'nextId': "corridor_darkness_return"} 
        ]
    },
    'check_barrels': {
        'location': "Кладовая",
        'narrative': "Вы осматриваете бочки и находите склянку с красной жидкостью.",
        'narrativeAfterGained': "Бочки пусты.",
        'itemGained': {'name': "лечебное зелье", 'description': "Восстанавливает здоровье.", 'quantity': 1, 'useEffect': {'narrative': "Вы выпиваете зелье.", 'healthChange': 25}},
        'choices': [
            {'text': "Взять плащ", 'nextId': "take_cloak", 'forbiddenItem': "старый плащ"},
            {'text': "Выйти в коридор", 'nextId': "corridor_darkness_return"} 
        ]
    },
    'corridor_darkness_return': {
        'location': "Темный коридор",
        'narrative': "Вы снова в темном коридоре.",
        'choices': [
            {'text': "Идти дальше", 'nextId': "armory_door"},
        ]
    },
    'armory_door': {
        'location': "Коридор",
        'narrative': "Вы доходите до массивной дубовой двери с символом скрещенных мечей.",
        'choices': [
            {'text': "Войти", 'nextId': "armory_fight"},
        ]
    },
    'armory_fight': {
        'location': "Оружейная",
        'narrative': "Внутри одинокий скелет-страж поворачивается в вашу сторону и медленно идет на вас.",
        'choices': [
            {'text': "Атаковать", 'nextId': "armory_fight_fists"},
            {'text': "Искать оружие", 'nextId': "armory_find_weapon"},
        ]
    },
    'armory_fight_fists': {
        'location': "Оружейная",
        'narrative': "Вы бросаетесь на скелета, но ваши кулаки бессильны. Скелет наносит вам рубящий удар мечом.",
        'healthChange': -40,
        'choices': [
            {'text': "Искать оружие", 'nextId': "armory_find_weapon"},
        ]
    },
    'armory_find_weapon': {
        'location': "Оружейная",
        'narrative': "Вы уворачиваетесь и осматриваетесь. На стойке у стены вы видите ржавый меч. Вы хватаете его.",
        'narrativeAfterGained': "Вы уже вооружены.",
        'itemGained': {'name': "ржавый меч", 'description': "Старый, но острый меч.", 'quantity': 1, 'slot': 'weapon', 'attackBonus': 10},
        'choices': [
            {'text': "Атаковать мечом", 'nextId': "armory_fight_success", 'requiredItem': "ржавый меч"},
        ]
    },
    'armory_fight_success': {
        'location': "Оружейная",
        'narrative': "Вооружившись, вы парируете удар и наносите ответный. Скелет с грохотом рассыпается на кости. Среди них вы замечаете щит. Путь свободен.",
        'itemGained': {'name': "прочный щит", 'description': "Надежный щит.", 'quantity': 1, 'slot': 'shield', 'defenseBonus': 15},
        'choices': [
            {'text': "Покинуть темницу", 'nextId': "final_win"},
        ]
    },
     'death_by_wounds': {
        'location': "Где-то в темноте",
        'narrative': "Ваши раны оказались слишком серьезными. Силы покидают вас...",
        'choices': [],
        'gameOver': {'isOver': True, 'message': "Вы погибли от полученных ран."}
    },
    'final_win': {
        'location': "Свобода",
        'narrative': "Вы толкаете тяжелую дверь и вдыхаете свежий ночной воздух. Вы свободны!",
        'choices': [],
        'gameOver': {'isOver': True, 'message': "Поздравляем! Вы прошли игру."}
    }
}


class GameState:
    """Хранит все изменяемые данные игры."""
    def __init__(self):
        self.reset()


    def reset(self):
        self.current_node_id = 'start'
        self.inventory = {}
        self.equipped_items = {'weapon': None, 'shield': None, 'torso': None}
        self.health = 100
        self.max_health = 100
        self.collected_item_nodes = set()
        self.game_over = False
        self.notification = None
        self.notification_time = 0


    def add_item(self, item_details):
        name = item_details['name']
        if name in self.inventory:
            self.inventory[name]['quantity'] += item_details.get('quantity', 1)
        else:
            self.inventory[name] = item_details.copy()
            if 'quantity' not in self.inventory[name]:
                self.inventory[name]['quantity'] = 1
        self.set_notification(f"Вы получили: {name}")


    def remove_item(self, item_name):
        if item_name in self.inventory:
            self.inventory[item_name]['quantity'] -= 1
            if self.inventory[item_name]['quantity'] <= 0:
                del self.inventory[item_name]


    def has_item(self, item_name):
        if item_name in self.inventory:
            return True
        for item in self.equipped_items.values():
            if item and item['name'] == item_name:
                return True
        return False


    def calculate_stats(self):
        base_attack = 5
        base_defense = 0
        attack_bonus = sum(item.get('attackBonus', 0) for item in self.equipped_items.values() if item)
        defense_bonus = sum(item.get('defenseBonus', 0) for item in self.equipped_items.values() if item)
        return {'attack': base_attack + attack_bonus, 'defense': base_defense + defense_bonus}
    

    def set_notification(self, message):
        self.notification = message
        self.notification_time = time.time()


    def unequip_item(self, slot):
        if self.equipped_items[slot]:
            item = self.equipped_items[slot]
            self.add_item(item)
            self.equipped_items[slot] = None
            self.set_notification(f"Вы сняли: {item['name']}")
            return True
        return False


# --- Функции отрисовки ---
def draw_text(text, font, color, surface, x, y, max_width=None):
    """Отрисовывает текст, с возможностью переноса строк."""
    if max_width:
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            # Проверка ширины строки
            if font.size(current_line + " " + word)[0] < max_width:
                current_line += " " + word
            else:
                lines.append(current_line.strip())
                current_line = word
        lines.append(current_line.strip())
        
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            surface.blit(text_surface, (x, y + i * font.get_linesize()))
    else:
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (x, y))


def draw_main_menu(buttons):
    """Отрисовывает главное меню."""
    screen.fill(BG_COLOR)
    title_text = "Эхо Забвения"
    title_w, title_h = HEADER_FONT.size(title_text)
    draw_text(title_text, HEADER_FONT, ACCENT_COLOR, screen, SCREEN_WIDTH // 2 - title_w // 2, 150)
    
    mouse_pos = pygame.mouse.get_pos()
    for key, button_rect in buttons.items():
        color = CHOICE_HOVER_COLOR if button_rect.collidepoint(mouse_pos) else CHOICE_BG_COLOR
        pygame.draw.rect(screen, color, button_rect, border_radius=10)
        
        text_w, text_h = UI_FONT.size(key)
        draw_text(key, UI_FONT, TEXT_COLOR, screen, button_rect.centerx - text_w // 2, button_rect.centery - text_h // 2)


def draw_game_screen(game_state, choice_buttons):
    """Отрисовывает основной игровой экран."""
    screen.fill(BG_COLOR)
    
    # --- Хедер ---
    stats = game_state.calculate_stats()
    node = STORY[game_state.current_node_id]
    draw_text(f"Локация: {node['location']}", UI_FONT, ACCENT_COLOR, screen, 50, 30)
    
    # --- Полоска здоровья (ИСПРАВЛЕННЫЙ БЛОК) ---
    hp_bar_width = 300
    hp_ratio = game_state.health / game_state.max_health
    if hp_ratio < 0: hp_ratio = 0
    
    # Координаты полоски
    bar_x = SCREEN_WIDTH - hp_bar_width - 50
    bar_y = 30
    bar_height = 25
    
    # Рисуем саму полоску
    pygame.draw.rect(screen, RED, (bar_x, bar_y, int(hp_bar_width * hp_ratio), bar_height))
    pygame.draw.rect(screen, TEXT_COLOR, (bar_x, bar_y, hp_bar_width, bar_height), 2)
    
    # Формируем текст HP
    hp_text = f"HP: {game_state.health}/{game_state.max_health}"
    
    # Вычисляем размеры текста, чтобы расположить его ровно слева
    text_w, text_h = UI_FONT.size(hp_text)
    
    # Позиция текста: Слева от начала бара минус 15 пикселей (отступ)
    text_x = bar_x - text_w - 15
    # Центрируем текст по вертикали относительно высоты бара
    text_y = bar_y + (bar_height - text_h) // 2 
    
    draw_text(hp_text, UI_FONT, TEXT_COLOR, screen, text_x, text_y)
    
    # Статы
    draw_text(f"Атака: {stats['attack']} / Защита: {stats['defense']}", UI_FONT, TEXT_COLOR, screen, 50, 65)
    
    # --- Основной текст ---
    narrative_to_show = node['narrative']
    if 'itemGained' in node and game_state.current_node_id in game_state.collected_item_nodes and 'narrativeAfterGained' in node:
        narrative_to_show = node['narrativeAfterGained']
    draw_text(narrative_to_show, NARRATIVE_FONT, TEXT_COLOR, screen, 50, 150, max_width=SCREEN_WIDTH - 100)

    # --- Кнопки выбора ---
    mouse_pos = pygame.mouse.get_pos()
    for text, rect in choice_buttons.items():
        color = CHOICE_HOVER_COLOR if rect.collidepoint(mouse_pos) else CHOICE_BG_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=8)
        draw_text(text, CHOICE_FONT, TEXT_COLOR, screen, rect.x + 15, rect.y + 10, max_width=rect.width - 30)

    # --- Уведомление ---
    if game_state.notification and (time.time() - game_state.notification_time < 3):
        draw_text(game_state.notification, UI_FONT, GREEN, screen, 50, SCREEN_HEIGHT - 50)


def draw_inventory(game_state, buttons):
    screen.fill(BG_COLOR)
    draw_text("Инвентарь", HEADER_FONT, ACCENT_COLOR, screen, 50, 30)
    
    # --- Экипировка ---
    draw_text("Экипировка", UI_FONT, ACCENT_COLOR, screen, 50, 120)
    y_offset = 160
    for slot, item in game_state.equipped_items.items():
        item_name = item['name'] if item else "Пусто"
        item_desc = ""
        if item:
            if 'attackBonus' in item:
                item_desc = f" +{item['attackBonus']} атк"
            if 'defenseBonus' in item:
                item_desc = f" +{item['defenseBonus']} защита"
        
        # Кнопка для снятия предмета
        if item:
            button_key = f"unequip_{slot}"
            buttons[button_key] = pygame.Rect(50, y_offset - 5, 400, 30)
            
            color = CHOICE_HOVER_COLOR if buttons[button_key].collidepoint(pygame.mouse.get_pos()) else BG_COLOR
            pygame.draw.rect(screen, color, buttons[button_key], border_radius=5)
            
            text = f"{slot.capitalize()}: {item_name}{item_desc} (нажмите, чтобы снять)"
            draw_text(text, UI_FONT, TEXT_COLOR, screen, 70, y_offset)
        else:
            text = f"{slot.capitalize()}: {item_name}"
            draw_text(text, UI_FONT, TEXT_COLOR, screen, 70, y_offset)
        
        y_offset += 40
        
    # --- Рюкзак ---
    draw_text("Рюкзак", UI_FONT, ACCENT_COLOR, screen, 500, 120)
    y_offset = 160
    for item_name, item_details in game_state.inventory.items():
        item_desc = f" - {item_details['description']}"
        if 'attackBonus' in item_details:
            item_desc += f" (+{item_details['attackBonus']} атк)"
        if 'defenseBonus' in item_details:
            item_desc += f" (+{item_details['defenseBonus']} защита)"
        if 'useEffect' in item_details:
            item_desc += f" (лечение: +{item_details['useEffect']['healthChange']})"
            
        text = f"{item_name} (x{item_details['quantity']}){item_desc}"
        button_key = f"item_{item_name}"
        # Исправляем ширину кнопок в инвентаре, чтобы текст влезал
        buttons[button_key] = pygame.Rect(520, y_offset - 5, 480, 30)
        
        color = CHOICE_HOVER_COLOR if buttons[button_key].collidepoint(pygame.mouse.get_pos()) else BG_COLOR
        pygame.draw.rect(screen, color, buttons[button_key], border_radius=5)
        # Отрисовка с ограничением ширины, чтобы не вылезало за экран
        draw_text(text, UI_FONT, TEXT_COLOR, screen, 530, y_offset, max_width=460)
        y_offset += 40
        
    # Кнопка назад
    buttons['back'] = pygame.Rect(50, SCREEN_HEIGHT - 100, 200, 50)
    color = CHOICE_HOVER_COLOR if buttons['back'].collidepoint(pygame.mouse.get_pos()) else CHOICE_BG_COLOR
    pygame.draw.rect(screen, color, buttons['back'], border_radius=10)
    
    back_w, back_h = UI_FONT.size("Назад")
    draw_text("Назад", UI_FONT, TEXT_COLOR, screen, buttons['back'].centerx - back_w // 2, buttons['back'].centery - back_h // 2)


# --- Основной цикл ---
def main():
    game_state = GameState()
    clock = pygame.time.Clock()
    current_screen = "MAIN_MENU" # MAIN_MENU, GAME, INVENTORY
    
    # --- Создание кнопок для меню ---
    main_menu_buttons = {
        "Начать игру": pygame.Rect(SCREEN_WIDTH // 2 - 150, 350, 300, 60),
        "Выход": pygame.Rect(SCREEN_WIDTH // 2 - 150, 430, 300, 60)
    }

    choice_buttons = {}
    inventory_buttons = {}

    running = True
    while running:
        # --- Обработка событий ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Левая кнопка мыши
                    if current_screen == "MAIN_MENU":
                        for text, rect in main_menu_buttons.items():
                            if rect.collidepoint(event.pos):
                                if text == "Начать игру":
                                    game_state.reset()
                                    current_screen = "GAME"
                                elif text == "Выход":
                                    running = False
                    
                    elif current_screen == "GAME":
                        # Проверка на нажатие кнопки инвентаря
                        inventory_button_rect = pygame.Rect(SCREEN_WIDTH - 200, 65, 150, 40)
                        if inventory_button_rect.collidepoint(event.pos):
                            current_screen = "INVENTORY"
                            continue
                            
                        # Проверка на кнопку возврата в меню (в состоянии game over)
                        if game_state.game_over:
                            back_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 450, 200, 50)
                            if back_button.collidepoint(event.pos):
                                current_screen = "MAIN_MENU"
                            continue
                            
                        # Обработка обычных выборов
                        for text, rect in choice_buttons.items():
                            if rect.collidepoint(event.pos):
                                node = STORY[game_state.current_node_id]
                                for choice_data in node['choices']:
                                    if choice_data['text'] == text:
                                        game_state.current_node_id = choice_data['nextId']
                                        next_node = STORY[game_state.current_node_id]

                                        if 'healthChange' in next_node:
                                            game_state.health = max(0, game_state.health + next_node['healthChange'])
                                        if 'itemGained' in next_node and game_state.current_node_id not in game_state.collected_item_nodes:
                                            game_state.add_item(next_node['itemGained'])
                                            game_state.collected_item_nodes.add(game_state.current_node_id)
                                        if 'itemLost' in next_node:
                                            game_state.remove_item(next_node['itemLost'])
                                        
                                        if game_state.health <= 0:
                                            game_state.current_node_id = 'death_by_wounds'

                                        if 'gameOver' in STORY[game_state.current_node_id]:
                                            game_state.game_over = True
                                        
                                        break

                    elif current_screen == "INVENTORY":
                        if inventory_buttons['back'].collidepoint(event.pos):
                            current_screen = "GAME"
                        else:
                            for key, rect in inventory_buttons.items():
                                if key.startswith("unequip_") and rect.collidepoint(event.pos):
                                    slot = key.split("_", 1)[1] # Исправлено деление строки
                                    game_state.unequip_item(slot)
                                elif key.startswith("item_") and rect.collidepoint(event.pos):
                                    item_name = key.split("_", 1)[1] # Исправлено деление строки
                                    item = game_state.inventory.get(item_name)
                                    if item:
                                        if 'useEffect' in item:
                                            effect = item['useEffect']
                                            game_state.health = min(game_state.max_health, game_state.health + effect['healthChange'])
                                            game_state.remove_item(item_name)
                                            game_state.set_notification(f"Вы использовали: {item_name}")
                                        elif 'slot' in item:
                                            slot = item['slot']
                                            if game_state.equipped_items[slot]:
                                                game_state.add_item(game_state.equipped_items[slot])
                                            game_state.equipped_items[slot] = item
                                            game_state.remove_item(item_name)
                                            game_state.set_notification(f"Вы надели: {item_name}")
        
        # --- Отрисовка ---
        if current_screen == "MAIN_MENU":
            draw_main_menu(main_menu_buttons)
        
        elif current_screen == "GAME":
            # --- Генерация кнопок выбора ---
            choice_buttons.clear()
            node = STORY[game_state.current_node_id]
            
            if not game_state.game_over:
                y_offset = SCREEN_HEIGHT - (len(node['choices']) * 60) - 40
                for choice in node['choices']:
                    if 'requiredItem' in choice and not game_state.has_item(choice['requiredItem']):
                        continue
                    if 'forbiddenItem' in choice and game_state.has_item(choice['forbiddenItem']):
                        continue
                    
                    button_rect = pygame.Rect(50, y_offset, SCREEN_WIDTH - 100, 50)
                    choice_buttons[choice['text']] = button_rect
                    y_offset += 60
            
            draw_game_screen(game_state, choice_buttons)
            
            # Кнопка инвентаря
            inventory_button_rect = pygame.Rect(SCREEN_WIDTH - 200, 65, 150, 40)
            color = CHOICE_HOVER_COLOR if inventory_button_rect.collidepoint(pygame.mouse.get_pos()) else CHOICE_BG_COLOR
            pygame.draw.rect(screen, color, inventory_button_rect, border_radius=8)
            
            inv_text = "Инвентарь"
            inv_w, inv_h = UI_FONT.size(inv_text)
            draw_text(inv_text, UI_FONT, TEXT_COLOR, screen, inventory_button_rect.centerx - inv_w // 2, inventory_button_rect.centery - inv_h // 2)

            # Если игра окончена
            if game_state.game_over:
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                s.fill((0,0,0, 180))
                screen.blit(s, (0,0))
                message = STORY[game_state.current_node_id]['gameOver']['message']
                
                msg_w, msg_h = HEADER_FONT.size("Игра окончена")
                draw_text("Игра окончена", HEADER_FONT, RED, screen, SCREEN_WIDTH//2 - msg_w//2, 250)
                
                desc_w, desc_h = UI_FONT.size(message)
                draw_text(message, UI_FONT, TEXT_COLOR, screen, SCREEN_WIDTH//2 - desc_w//2, 350)
                
                # Кнопка возврата в меню
                back_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 450, 200, 50)
                color = CHOICE_HOVER_COLOR if back_button.collidepoint(pygame.mouse.get_pos()) else CHOICE_BG_COLOR
                pygame.draw.rect(screen, color, back_button, border_radius=10)
                
                menu_w, menu_h = UI_FONT.size("В меню")
                draw_text("В меню", UI_FONT, TEXT_COLOR, screen, back_button.centerx - menu_w//2, back_button.centery - menu_h//2)

        elif current_screen == "INVENTORY":
            inventory_buttons.clear()
            draw_inventory(game_state, inventory_buttons)

        pygame.display.flip()
        clock.tick(30) # Ограничение до 30 кадров в секунду

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
