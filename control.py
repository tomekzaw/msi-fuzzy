try:
    import numpy as np
    import skfuzzy as fuzz
    from skfuzzy import control as ctrl
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
except ModuleNotFoundError as e:
    print(e)
    raise SystemExit('Please run `pip install -r requirements.txt`')

if __name__ == '__main__':
    from utils import fix_scaling
    fix_scaling()

speed = ctrl.Antecedent(np.arange(0, 70, 1), 'speed')  # in km/h
distance = ctrl.Antecedent(np.arange(0, 250, 5), 'distance')  # in metres
occupancy = ctrl.Antecedent(np.arange(0, 70, 5), 'occupancy')  # number of passengers
# TODO: visibility, wet rails

acceleration = ctrl.Consequent(np.arange(-20, 5, 1), 'acceleration')  # in km/h/s

speed['stopping'] = fuzz.trimf(speed.universe, [0, 0, 2])
speed['slow'] = fuzz.trimf(speed.universe, [0, 10, 20])
speed['medium'] = fuzz.trimf(speed.universe, [15, 25, 40])
speed['fast'] = fuzz.trimf(speed.universe, [35, 50, 60])
speed['too_fast'] = fuzz.trimf(speed.universe, [55, 70, 70])

distance['close'] = fuzz.trimf(distance.universe, [0, 0, 20])
distance['approaching'] = fuzz.trimf(distance.universe, [10, 40, 80])
distance['in_sight'] = fuzz.trimf(distance.universe, [60, 130, 200])
distance['far'] = fuzz.trimf(distance.universe, [150, 250, 250])

occupancy['empty'] = fuzz.trimf(occupancy.universe, [0, 0, 70])
occupancy['full'] = fuzz.trimf(occupancy.universe, [0, 70, 70])

acceleration['break_emergency'] = fuzz.trimf(acceleration.universe, [-20, -20, -10])
acceleration['break_hard'] = fuzz.trimf(acceleration.universe, [-15, -10, -5])
acceleration['break_gently'] = fuzz.trimf(acceleration.universe, [-8, -5, 0])
acceleration['maintain'] = fuzz.trimf(acceleration.universe, [-1, 0, 1])
acceleration['accelerate'] = fuzz.trimf(acceleration.universe, [0, 5, 5])

if __name__ == '__main__':
    speed.view()
    distance.view()
    occupancy.view()
    acceleration.view()

rules = [
    ctrl.Rule(distance['far'], acceleration['accelerate']),

    ctrl.Rule(occupancy['empty'] & speed['too_fast'] & distance['far'], acceleration['break_hard']),
    ctrl.Rule(occupancy['full'] & speed['too_fast'] & distance['far'], acceleration['break_gently']),

    ctrl.Rule(speed['too_fast'] & ~distance['far'], acceleration['break_emergency']),

    ctrl.Rule(speed['fast'] & distance['close'], acceleration['break_emergency']),
    ctrl.Rule(occupancy['empty'] & speed['fast'] & distance['approaching'], acceleration['break_hard']),
    ctrl.Rule(occupancy['full'] & speed['fast'] & distance['approaching'], acceleration['break_gently']),
    ctrl.Rule(speed['fast'] & distance['in_sight'], acceleration['break_gently']),

    ctrl.Rule(speed['medium'] & distance['close'], acceleration['break_emergency']),
    ctrl.Rule(occupancy['empty'] & speed['medium'] & distance['approaching'], acceleration['break_hard']),
    ctrl.Rule(occupancy['full'] & speed['medium'] & distance['approaching'], acceleration['break_gently']),
    ctrl.Rule(occupancy['empty'] & speed['medium'] & ~(distance['close'] | distance['approaching']), acceleration['maintain']),
    ctrl.Rule(occupancy['full'] & speed['medium'] & ~(distance['close'] | distance['approaching']), acceleration['break_gently']),

    ctrl.Rule(speed['slow'] & distance['close'], acceleration['break_gently']),
    ctrl.Rule(speed['slow'] & distance['approaching'], acceleration['maintain']),
    ctrl.Rule(speed['slow'] & ~(distance['close'] | distance['approaching']), acceleration['accelerate']),

    ctrl.Rule(speed['stopping'] & distance['close'], acceleration['break_hard']),
    ctrl.Rule(speed['stopping'] & ~distance['close'], acceleration['accelerate']),
]

system = ctrl.ControlSystem(rules)
simulation = ctrl.ControlSystemSimulation(system)

def calculate_acceleration_kmhs(speed_kmh, distance_m, occupancy_p):
    simulation.input['speed'] = speed_kmh
    simulation.input['distance'] = distance_m
    simulation.input['occupancy'] = occupancy_p
    simulation.compute()
    return simulation.output['acceleration']

if __name__ == '__main__':
    calculate_acceleration_kmhs(40, 100, 10)
    acceleration.view(sim=simulation)

if __name__ == '__main__':
    plt.show()
