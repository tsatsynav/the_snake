"""Игра «Змейка» на Pygame."""
import sys
from random import choice, randint

import pygame as pg

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

# Базовые цвета:
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
LIGHT_BLUE = (93, 216, 228)

# Цвет фона поля:
BOARD_BACKGROUND_COLOR = BLACK
# Цвет границы ячейки:
BORDER_COLOR = LIGHT_BLUE
# Цвет яблока:
APPLE_COLOR = RED
# Цвет змейки:
SNAKE_COLOR = GREEN

# Скорость движения змейки:
SPEED = 20

# Начальная позиция игровых объектов — центр экрана:
START_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')
# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=START_POSITION, body_color=None):
        """Инициализирует базовые атрибуты игрового объекта.

        Args:
            position: позиция объекта на игровом поле.
            body_color: цвет объекта.
        """
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект (переопределяется в наследниках)."""
        raise NotImplementedError(
            f'Метод draw не переопределён в классе '
            f'{self.__class__.__name__}.'
        )

    def draw_cell(self, position, color, border=True):
        """Отрисовывает одну ячейку игрового поля.

        Args:
            position: координаты верхнего левого угла ячейки.
            color: цвет заливки ячейки.
            border: нужно ли рисовать границу ячейки.
        """
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        if border:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс, описывающий яблоко на игровом поле."""

    def __init__(self, occupied_positions=None, body_color=APPLE_COLOR):
        """Создаёт яблоко и задаёт ему случайную позицию.

        Args:
            occupied_positions: занятые позиции, куда нельзя ставить яблоко.
            body_color: цвет яблока.
        """
        super().__init__(body_color=body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=None):
        """Устанавливает случайную позицию яблока на игровом поле.

        Args:
            occupied_positions: занятые позиции, куда нельзя ставить яблоко.
        """
        if occupied_positions is None:
            occupied_positions = []
        while True:
            new_position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if new_position not in occupied_positions:
                self.position = new_position
                return

    def draw(self):
        """Отрисовывает яблоко на игровом экране."""
        self.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение."""

    def __init__(self, body_color=SNAKE_COLOR):
        """Инициализирует начальное состояние змейки.

        Args:
            body_color: цвет змейки.
        """
        super().__init__(body_color=body_color)
        self.reset(initial_direction=RIGHT)

    def update_direction(self, new_direction):
        """Обновляет направление движения змейки.

        Новое направление применяется, только если оно не противоположно
        текущему: змейка не может двигаться назад.

        Args:
            new_direction: новое направление движения.
        """
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.direction = new_direction

    def move(self):
        """Обновляет позицию змейки, перемещая её на одну ячейку."""
        head = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head[0] + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head[1] + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        self.last = (
            self.positions.pop()
            if len(self.positions) > self.length
            else None
        )

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self, initial_direction=None):
        """Сбрасывает змейку в начальное состояние.

        Args:
            initial_direction: начальное направление движения змейки.
                Если не задано, направление выбирается случайно.
        """
        self.length = 1
        self.positions = [self.position]
        if initial_direction is None:
            initial_direction = choice([UP, DOWN, LEFT, RIGHT])
        self.direction = initial_direction
        self.last = None

    def draw(self):
        """Отрисовывает змейку на игровом экране."""
        self.draw_cell(self.get_head_position(), self.body_color)
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR, border=False)


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш и меняет направление змейки.

    Args:
        game_object: объект Snake, для которого меняется направление.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP:
                game_object.update_direction(UP)
            elif event.key == pg.K_DOWN:
                game_object.update_direction(DOWN)
            elif event.key == pg.K_LEFT:
                game_object.update_direction(LEFT)
            elif event.key == pg.K_RIGHT:
                game_object.update_direction(RIGHT)
            elif event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()


def main():
    """Запускает основной игровой цикл."""
    pg.init()
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() in snake.positions[4:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)

        snake.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
