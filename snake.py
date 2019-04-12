import collections
import random

import pygame


class Window:
    def __init__(self, win_width, win_height, tiles_horizontal, tiles_vertical):
        self.tiles_horizontal = tiles_horizontal
        self.tiles_vertical = tiles_vertical
        self.win_width = win_width
        self.win_height = win_height
        self.tile_height = win_height / self.tiles_vertical
        self.tile_width = win_width / self.tiles_horizontal
        self.diagonal = ((win_height - 0) ** 2 + (win_width - 1) ** 2) ** (1 / 2)
        self.diagonal_tiles = ((tiles_horizontal - 0) ** 2 + (tiles_vertical - 1) ** 2) ** (1 / 2)

        self.speed = 100
        self.food = None
        self.win = pygame.display.set_mode((self.win_width, self.win_height))

    def generate_food(self):
        self.food = self.random_tile()

    def random_tile(self):
        i = random.randrange(self.tiles_horizontal)
        j = random.randrange(self.tiles_vertical)
        return i, j

    @staticmethod
    def update():
        pygame.display.update()

    def clear(self):
        self.win.fill((0, 0, 0))

    def delay(self):
        if self.speed != 0:
            pygame.time.delay(200 // self.speed)


class Snake:
    def __init__(self, window):
        self.window = window
        pygame.init()

        pygame.display.set_caption("The Snake!")

        x = self.window.tiles_horizontal // 2
        y = self.window.tiles_vertical // 2
        self.snake = collections.deque([(x, y), (x - 1, y), (x - 2, y), (x - 3, y)])

        self.snake_length = 4
        self.direction = 1
        self.color = random.randrange(50, 255), random.randrange(50, 255), random.randrange(50, 255)

    def reset(self):
        x = self.window.tiles_horizontal // 2
        y = self.window.tiles_vertical // 2
        self.snake = collections.deque([(x, y), (x - 1, y), (x - 2, y), (x - 3, y)])

        self.snake_length = 4
        self.direction = 1

    def step(self, action):
        # self.window.delay()
        reward = 1

        if not self.window.food:
            self.window.generate_food()

        x, y = self.tile_to_window_coords(self.window.food)
        pygame.draw.rect(self.window.win, (255, 0, 0),
                         (x, y, self.window.win_width / self.window.tiles_horizontal,
                          self.window.win_height / self.window.tiles_vertical))

        for tile in self.snake:
            x, y = self.tile_to_window_coords(tile)
            pygame.draw.rect(self.window.win, self.color, (
                x, y, self.window.win_width / self.window.tiles_horizontal,
                self.window.win_height / self.window.tiles_vertical))

        if action == 3 and self.direction != 1:
            self.direction = 3
        if action == 1 and self.direction != 3:
            self.direction = 1
        if action == 0 and self.direction != 2:
            self.direction = 0
        if action == 2 and self.direction != 0:
            self.direction = 2

        # if self.lose():
        #     self.reset()

        self.snake.appendleft(self.get_next())
        if len(self.snake) > self.snake_length:
            self.snake.pop()

        if self.snake[0] == self.window.food:
            reward = 1000
            self.window.food = None
            self.snake_length += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        return self.observe(), reward, self.lose()

    def tile_to_window_coords(self, tile):
        return tile[0] * self.window.tile_width, tile[1] * self.window.tile_height

    def get_next(self):
        x, y = self.head()
        if self.direction == 0:
            return x, y - 1
        elif self.direction == 1:
            return x + 1, y
        elif self.direction == 2:
            return x, y + 1
        elif self.direction == 3:
            return x - 1, y

    def hit_wall(self):
        x0, y0 = self.head()

        hit_up = x0 < 0 or y0 < 0
        hit_down = x0 > self.window.tiles_horizontal or y0 > self.window.tiles_vertical

        hit_right = self.is_left_tile(self.snake[0]) and self.is_right_tile(self.snake[1])
        hit_left = self.is_right_tile(self.snake[0]) and self.is_left_tile(self.snake[1])

        return hit_up or hit_down or hit_right or hit_left

    def lose(self):
        return self.head() in self.body() or self.hit_wall()

    @staticmethod
    def is_left_tile(tile):
        return tile[0] == 0

    def is_right_tile(self, tile):
        return tile[1] == self.window.tiles_horizontal - 1

    def head(self):
        return self.snake[0]

    def body(self):
        snake_body = self.snake.copy()
        snake_body.popleft()
        return snake_body

    def tile_in_window(self, tile):
        is_inside = 0 <= tile[0] <= self.window.tiles_horizontal and 0 <= tile[1] <= self.window.tiles_vertical
        return is_inside

    def next_tile_in_direction(self, direction, tile):
        x, y = tile[0], tile[1]
        if direction == 0:
            y -= 1
        elif direction == 1:
            x += 1
        elif direction == 2:
            y += 1
        elif direction == 3:
            x -= 1
        elif direction == 4:
            x += 1
            y -= 1
        elif direction == 5:
            x += 1
            y += 1
        elif direction == 6:
            x -= 1
            y += 1
        elif direction == 7:
            x -= 1
            y -= 1

        if self.tile_in_window((x, y)):
            return x, y
        else:
            return None

    @staticmethod
    def distance_between_tiles(tile1, tile2):
        return ((tile1[0] - tile2[0]) ** 2 + (tile1[1] - tile2[1]) ** 2) ** (1 / 2)

    def get_dimension(self, direction):
        if direction > 3:
            return self.window.diagonal_tiles
        elif direction % 2 == 0:
            return self.window.tiles_vertical
        else:
            return self.window.tiles_horizontal

    def observe(self):
        observations = [0.0] * 24
        for direction in range(0, 7):
            dim = self.get_dimension(direction)

            tile = self.head()
            while True:
                next_tile = self.next_tile_in_direction(direction, tile)
                if not next_tile:
                    observations[direction] = self.distance_between_tiles(self.head(), tile) / dim
                    break
                tile = self.next_tile_in_direction(direction, tile)

            tile = self.head()
            while True:
                next_tile = self.next_tile_in_direction(direction, tile)
                if not next_tile or next_tile in self.snake:
                    observations[direction + 8] = self.distance_between_tiles(self.head(), tile) / dim
                    break
                tile = self.next_tile_in_direction(direction, tile)

            tile = self.head()
            while True:
                next_tile = self.next_tile_in_direction(direction, tile)
                if not next_tile or next_tile in self.snake:
                    break
                elif next_tile == self.window.food:
                    observations[direction + 16] = 1 - self.distance_between_tiles(self.head(), tile) / dim

                tile = self.next_tile_in_direction(direction, tile)

        return observations
