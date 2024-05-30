import math
import heapq
from dataclasses import dataclass, field

@dataclass(order=True)
class SpriteMovement:
    sort_index: float = field(init=False, repr=False)
    x: float
    y: float
    radius: float

    def __post_init__(self):
        self.sort_index = (self.x, self.y)

@dataclass
class BattleEnvironment:
    width: float
    height: float
    entities: list

def distance(a: SpriteMovement, b: SpriteMovement) -> float:
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

def is_collision(a: SpriteMovement, b: SpriteMovement) -> bool:
    return distance(a, b) < (a.radius + b.radius)

def is_within_bounds(entity: SpriteMovement, env: BattleEnvironment) -> bool:
    return 0 <= entity.x <= env.width and 0 <= entity.y <= env.height

def is_valid_position(entity: SpriteMovement, env: BattleEnvironment) -> bool:
    if not is_within_bounds(entity, env):
        return False
    for other in env.entities:
        if is_collision(entity, other):
            return False
    return True

class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def is_empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]

def heuristic(a: SpriteMovement, b: SpriteMovement) -> float:
    return distance(a, b)

def a_star_search(env: BattleEnvironment, start: SpriteMovement, goal: SpriteMovement, movement_range: float):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[(start.x, start.y)] = None
    cost_so_far[(start.x, start.y)] = 0

    while not frontier.is_empty():
        current = frontier.get()

        if distance(current, goal) <= movement_range:
            path = []
            while current:
                path.append((current.x, current.y))
                current = came_from[(current.x, current.y)]
            path.reverse()
            return path

        for dx, dy in [(-movement_range, 0), (movement_range, 0), (0, -movement_range), (0, movement_range),
                       (-movement_range, -movement_range), (-movement_range, movement_range), (movement_range, -movement_range), (movement_range, movement_range)]:
            next_pos = SpriteMovement(current.x + dx, current.y + dy, start.radius)
            new_cost = cost_so_far[(current.x, current.y)] + movement_range
            if is_valid_position(next_pos, env):
                if (next_pos.x, next_pos.y) not in cost_so_far or new_cost < cost_so_far[(next_pos.x, next_pos.y)]:
                    cost_so_far[(next_pos.x, next_pos.y)] = new_cost
                    priority = new_cost + heuristic(next_pos, goal)
                    frontier.put(next_pos, priority)
                    came_from[(next_pos.x, next_pos.y)] = current

    return None  # If no path is found