from position import Position


class Item:
    def __init__(self, state, position: Position, tile):
        self.state = state
        self.position = position
        self.tile = tile


class Liquid(Item):
    def __init__(self, state, position, tile):
        super().__init__(state, position, tile)
        self.speed = 1


class Block(Item):
    def __init__(self, state, position, tile):
        super().__init__(state, position, tile)
        self.speed = 1


class Player(Item):
    def __init__(self, state, position, tile):
        super().__init__(state, position, tile)
        self.status = "alive"
        self.speed = 1


class Timer(Item):
    def __init__(self, state, position, tile, duration):
        super().__init__(state, position, tile)
        self.duration = duration
