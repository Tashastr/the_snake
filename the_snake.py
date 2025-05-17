from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()

# Переменная для цикла While




class GameObject:
    """Базовый класс для всех игровых объектов.
    Содержит общие свойства и методы для объектов игры, таких как змейка и
    яблоко.
    Атрибуты:
        position (tuple): Координаты объекта на экране (x, y).
        body_color (tuple): Цвет объекта в формате RGB (по умолчанию None).
    """

    def __init__(self) -> None:
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.body_color = None

    def draw(self):
        """Отрисовывает объект на экране.
        Должен быть переопределен в дочерних классах.
        """


class Apple(GameObject):
    """Класс, представляющий яблоко в игре 'Змейка'.
    Наследуется от GameObject и добавляет специфичные для яблока свойства:
    - Автоматическую установку случайной позиции при создании
    - Заданный цвет (APPLE_COLOR)

    Attributes:
        body_color (tuple): Цвет яблока в формате RGB, по умолчанию
        APPLE_COLOR.
        position (tuple): Текущие координаты яблока на игровом поле
        (наследуется от GameObject).
    """

    def __init__(self, snake = None):
        super().__init__()
        self.body_color = APPLE_COLOR
        self.snake = snake
        self.randomize_position()


    def draw(self):
        """Отрисовывает яблоко на игровом экране.

        Создает прямоугольник в позиции self.position и рисует его:
        - Основной цвет: self.body_color (APPLE_COLOR)
        - Граница: BORDER_COLOR (1 пиксель)

        Использует:
            pygame.Rect - для создания прямоугольника
            pygame.draw.rect - для отрисовки
        """
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self):
        """Устанавливает случайную позицию яблока на игровом поле.

        Позиция вычисляется:
        - По сетке GRID_SIZE (20x20 пикселей)
        - В пределах экрана (SCREEN_WIDTH, SCREEN_HEIGHT)
        - С учетом размера самого яблока (GRID_SIZE)

        Использует:
            randint - для генерации случайных координат
        """
        self.position = (
            (randint(0, (SCREEN_WIDTH - GRID_SIZE) // 20) * GRID_SIZE),
            (randint(0, (SCREEN_HEIGHT - GRID_SIZE) // 20) * GRID_SIZE)
        )
        if self.snake:  
            while self.position in self.snake.positions:
                self.randomize_position()


class Snake(GameObject):
    """Класс, реализующий змейку в игре 'Змейка'.

    Наследуется от GameObject и управляет:
    - Перемещением змейки
    - Обработкой столкновений
    - Поеданием яблок
    - Изменением направления движения

    Attributes:
        length (int): Текущая длина змейки (количество сегментов).
        positions (list[tuple[int, int]]): Список координат сегментов змейки.
        direction (tuple[int, int]): Текущее направление движения
        (UP, DOWN, LEFT, RIGHT).
        next_direction (tuple[int, int]|None): Следующее направление
        (для плавной смены).
        body_color (tuple[int, int, int]): Цвет змейки в формате RGB.
        last (tuple[int, int]|None): Координаты последнего удаленного сегмента.
        apple (Apple): Ссылка на объект яблока для проверки столкновений.
    """

    def __init__(self):
        super().__init__()
        self.length = 1
        self.positions = [(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)]
        self.direction = DOWN
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.last = None
        
        

    def update_direction(self):
        """Обновляет текущее направление движения змейки.

        Если было установлено следующее направление (next_direction),
        применяет его и сбрасывает next_direction в None.
        Это обеспечивает плавную смену направления без пропуска кадров.

        Логика работы:
        - Проверяет наличие next_direction
        - Применяет новое направление
        - Сбрасывает next_direction
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Перемещает змейку в текущем направлении."""
        new_head = self.calculate_new_head_position()
        self.update_snake_body(new_head)

    def calculate_new_head_position(self):
        """Вычисляет новую позицию головы с учётом границ экрана."""
        x, y = self.get_head_position()
        dx, dy = self.direction

        new_x = (x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (y + dy * GRID_SIZE) % SCREEN_HEIGHT

        return (new_x, new_y)

    def update_snake_body(self, new_head):
        """Обновляет тело змейки после перемещения."""
        self.positions.insert(0, new_head)

        if self.check_apple_collision(new_head):
            self.handle_apple_collision()

        self.trim_tail_if_needed()

    def check_apple_collision(self, position):
        """Проверяет столкновение головы с яблоком."""
        return position == self.apple.position

    def handle_apple_collision(self):
        """Обрабатывает поедание яблока."""
        self.length += 1
        self.apple.randomize_position()

    def trim_tail_if_needed(self):
        """Удаляет хвостовой сегмент, если змейка не выросла."""
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self):
        """Отрисовывает все сегменты змейки на игровом экране.

        Метод выполняет следующие действия:
        1. Итерируется по всем сегментам змейки, кроме головы
        (последний элемент в positions)
        2. Для каждого сегмента создает прямоугольник (Rect) с размерами
        GRID_SIZE x GRID_SIZE
        3. Отрисовывает каждый сегмент в два этапа:
        - Основная заливка цветом self.body_color (зеленый по умолчанию)
        - Граница толщиной 1 пиксель цветом BORDER_COLOR (бирюзовый)

        Особенности:
        - Голова змейки (первый элемент positions) обрабатывается отдельно в
        другом методе
        - Использует глобальную переменную screen для отрисовки
        - Размер всех сегментов фиксирован и определяется GRID_SIZE

        Используемые технические элементы:
        - pygame.Rect: для представления прямоугольной области отрисовки
        - pygame.draw.rect: для непосредственной отрисовки на поверхности

        Note:
            Для корректной работы требуется предварительная инициализация:
            - pygame.display
            - Глобальной переменной screen
        """
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Возвращает текущие координаты головы змейки.

        Returns:
            tuple[int, int]: Координаты головы в формате (x, y), где:
                - x (int): горизонтальная позиция в пикселях
                - y (int): вертикальная позиция в пикселях

        Note:
            - Координаты берутся из первого элемента списка positions
            - Значения всегда кратны GRID_SIZE (размеру сетки)
            - Для пустой змейки вызовет IndexError

        Example:
            >>> snake = Snake(apple)
            >>> snake.get_head_position()
            (320, 240)  # Стандартная начальная позиция
        """
        return self.positions[0]

    def reset(self):
        """Сбрасывает состояние змейки при столкновении с самой собой.

        Проверяет и обрабатывает следующие условия:
        1. Если голова змейки пересекается с её телом (self.positions[0]
        встречается > 1 раза):
        - Очищает экран (заливает фоном BOARD_BACKGROUND_COLOR)
        - Сбрасывает длину змейки к начальному значению (1)
        - Возвращает змейку в центр экрана (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        - Задает случайное новое направление движения
        - Возвращает False (игра должна завершиться)

        2. Если столкновения нет:
        - Возвращает True (игра продолжается)

        Returns:
            bool: Флаг продолжения игры:
                - True: игра продолжается
                - False: произошло столкновение, игра должна завершиться

        Side Effects:
            - Модифицирует состояние экрана (очистка)
            - Изменяет основные атрибуты змейки (length, positions, direction)

        Note:
            В текущей реализации метод неявно зависит от глобальной переменной
            screen.
            Для полной инкапсуляции следует передавать screen как параметр.
        """
        if self.positions.count(self.positions[0]) > 1:
            screen.fill(BOARD_BACKGROUND_COLOR)
            self.length = 1
            self.positions = [(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)]
            self.direction = choice([DOWN, UP, LEFT, RIGHT])
        else:
            return True


def handle_keys(game_object):
    """Сбрасывает состояние змейки при столкновении с собой и возвращает
    статус игры.

    Действия при столкновении (голова пересекает тело):
    1. Очищает игровое поле (заливка цветом BOARD_BACKGROUND_COLOR)
    2. Сбрасывает параметры змейки:
       - Длина возвращается к 1 сегменту
       - Позиция - в центр экрана (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
       - Направление - случайное из возможных (UP, DOWN, LEFT, RIGHT)
    3. Возвращает False для завершения игры

    Returns:
        bool: Статус продолжения игры:
            - True: столкновения нет, игра продолжается
            - False: было столкновение, требуется завершение игры

    Side effects:
        - Изменяет состояние игрового экрана (очистка)
        - Модифицирует атрибуты змейки:
          * length
          * positions
          * direction

    Implementation notes:
        - Использует глобальную переменную screen (нарушение инкапсуляции)
        - Для улучшения архитектуры следует:
          1. Передавать screen как параметр
          2. Вынести логику сброса в отдельный метод
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основная функция игры 'Змейка', содержащая главный игровой цикл.

    Выполняет последовательность действий:
    1. Инициализирует движок Pygame
    2. Создает игровые объекты:
       - Яблоко (Apple)
       - Змейку (Snake), передавая ей яблоко для взаимодействия
    3. Запускает основной игровой цикл с контролем FPS (SPEED)
    4. В каждом кадре:
       - Обрабатывает пользовательский ввод
       - Отрисовывает игровые объекты
       - Обновляет состояние игры
       - Проверяет условия завершения

    Flow:
        Инициализация → Создание объектов → Главный цикл → Завершение

    Side effects:
        - Создает графическое окно через Pygame
        - Захватывает системные ресурсы для рендеринга
        - Обрабатывает события ввода с клавиатуры

    Example:
        Стандартный запуск игры:
        >>> if __name__ == '__main__':
        ...     main()
    """
    # Инициализация PyGame:
    pygame.init()
    snake = Snake()
    apple = Apple(snake)
    snake.apple = apple
    running = True
    while running:
        clock.tick(SPEED)
        handle_keys(snake)
        apple.draw()
        snake.draw()
        pygame.display.update()
        snake.update_direction()
        snake.move()
        snake.reset()

    pygame.quit()


if __name__ == '__main__':
    main()
