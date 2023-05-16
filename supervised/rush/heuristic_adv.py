class AdvancedHeuristic:
    def __init__(self, board_str):
        self.board_str = board_str
        self.grid_size = 6
        self.visited = set()
        self.car_sizes = {}
        self.car_positions = {}
        self.car_fixed_positions = {}
        self.car_orient = {}

    def get_value(self, state):
        self.state = state
        self.visited.clear()

        if self.is_goal(state):
            return 0

        return self.get_minimum_required_moves(state)

    # Check if the state is the goal state
    def is_goal(self, state):
        target_car = "AA"
        target_position = state.index(target_car)
        return target_position % self.grid_size == self.grid_size - len(target_car)

    # Calculate the minimum required moves for the given state
    def get_minimum_required_moves(self, state):
        self.visited.add("A")

        value = 1

        for car in self.get_initial_blocking_cars():
            needs_space_front = self.needs_space("A", car, 0, True)
            needs_space_back = self.needs_space("A", car, 0, False)

            value += self.get_blocking_value(car, needs_space_front, needs_space_back)

        return value

    # Get a list of cars that initially block the target car
    def get_initial_blocking_cars(self):
        blocking = []

        car_orient = self.car_orient(0)
        car_size = self.car_size(0)
        car_pos = self.variable_position(0)
        car_fixed = self.fixed_position(0)

        for i in range(1, self.num_cars):
            if car_orient == self.car_orient(i):
                continue

            i_fixed = self.fixed_position(i)

            if i_fixed < car_pos + car_size:
                continue

            i_pos = self.variable_position(i)
            i_pos_front = i_pos + self.car_size(i)

            if car_fixed >= i_pos and car_fixed < i_pos_front:
                blocking.append(i)

        return blocking
    
    


    # Get the blocking value for the current car
    def get_blocking_value(self, car, needs_space_front, needs_space_back):
        self.visited.add(car)

        value = 1

        for next_car in set(self.state.replace(".", "").replace(car, "")):
            if next_car == "A" or next_car in self.visited:
                continue

            if not self.is_intersecting(car, next_car):
                continue

            value_fwd = 0
            value_bwd = 0

            fwd_moveable = self.can_move(car, next_car, needs_space_front, True)
            bwd_moveable = self.can_move(car, next_car, needs_space_back, False)

            needs_space_fwd = self.needs_space(car, next_car, needs_space_front, True)
            needs_space_bwd = self.needs_space(car, next_car, needs_space_back, False)

            if not fwd_moveable:
                value_fwd = self.get_blocking_value(next_car, needs_space_fwd, needs_space_bwd)
            elif self.is_wall_blocking(car, needs_space_front, True):
                value_fwd = float('inf')

            if not bwd_moveable:
                value_bwd = self.get_blocking_value(next_car, needs_space_fwd, needs_space_bwd)
            elif self.is_wall_blocking(car, needs_space_back, False):
                value_bwd = float('inf')

            value += min(value_fwd, value_bwd)

        return value
    @property
    def num_cars(self):
        cars = set(self.board_str) - set(".")
        return len(cars)
    
    def car_orient(self, car):
        return car.isupper()

    def car_size(self, car):
        return self.board_str.count(car)

    def fixed_position(self, car):
        return self.board_str.index(car) // self.grid_size

    def variable_position(self, car):
        return self.board_str.index(car) % self.grid_size
    def is_intersecting(self, car1, car2):
        car1_positions = set([i for i, x in enumerate(self.state) if x == car1])
        car2_positions = set([i for i, x in enumerate(self.state) if x == car2])
        return bool(car1_positions.intersection(car2_positions))
    def can_move(self, car1, car2, needs_space, forward):
        car1_positions = [i for i, x in enumerate(self.state) if x == car1]
        car2_positions = [i for i, x in enumerate(self.state) if x == car2]

        if forward:
            return all(pos + needs_space not in car2_positions for pos in car1_positions)
        else:
            return all(pos - needs_space not in car2_positions for pos in car1_positions)

# Example usage
board_str = "..iBBB..ik..AAjk.lCCjDDlghEE.lghFF.."
heuristic = AdvancedHeuristic(board_str)
state = board_str
heuristic_value = heuristic.get_value(state)
print("Heuristic value for the given state:", heuristic_value)
