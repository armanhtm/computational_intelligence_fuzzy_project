# -*- coding: utf-8 -*-

# python imports
from math import degrees
# pyfuzzy imports
from fuzzy.storage.fcl.Reader import Reader

class FuzzyController:

    def __init__(self, fcl_path):
        self.system = Reader().load_from_file(fcl_path)

    def _make_input(self, world):
        return dict(
            cp=world.x,
            cv=world.v,
            pa=degrees(world.theta),
            pv=degrees(world.omega)
        )

    def _make_output(self):
        return dict(
            force=0.
        )

    def make_line_equation(self, points, x, max=1):
        if len(points) == 2:
            two_points = True
        else:
            two_points = False
        head = points[0][0]
        if two_points:
            tail = points[1][0]
        else:
            tail = points[2][0]
        if x > tail or x < head:
            return 0
        elif x <= points[1][0] or two_points:
            index = 0
        else:
            index = 1
        x0 = points[index][0]
        y0 = points[index][1]
        x1 = points[index + 1][0]
        y1 = points[index + 1][1]
        temp = ((((y1 - y0) * 1.0) / (x1 - x0)) * (x - x0)) + y0
        if temp >= max:
            return max
        else:
            return temp

    def fuzzify_pa(self, x):
        pa_list = [
            ["up_more_right", (0, 0), (30, 1), (60, 0)],
            ["up_right", (30, 0), (60, 1), (90, 0)],
            ["up", (60, 0), (90, 1), (120, 0)],
            ["up_left", (90, 0), (120, 1), (150, 0)],
            ["up_more_left", (120, 0), (150, 1), (180, 0)],
            ["down_more_left", (180, 0), (210, 1), (240, 0)],
            ["down_left", (210, 0), (240, 1), (270, 0)],
            ["down", (240, 0), (270, 1), (300, 0)],
            ["down_right", (270, 0), (300, 1), (330, 0)],
            ["down_more_right", (300, 0), (330, 1), (360, 0)]
        ]
        pa_list_second = [
            ["up_right", (0, 0), (45, 1), (90, 0)],
            ["up", (45, 0), (90, 1), (135, 0)],
            ["up_left", (90, 0), (135, 1), (180, 0)],
            ["down_left", (180, 0), (225, 1), (270, 0)],
            ["down", (225, 0), (270, 1), (315, 0)],
            ["down_right", (270, 0), (315, 1), (360, 0)],
        ]
        pa_fuzzy = {}
        for mood in pa_list:
            pa_fuzzy[mood[0]] = self.make_line_equation(mood[1:], x)
        return pa_fuzzy

    def fuzzify_pv(self, x):
        pv_list = [
            ["cw_fast", (-200, 1), (-100, 0)],
            ["cw_slow", (-200, 0), (-100, 1), (0, 0)],
            ["stop_pv", (-100, 0), (0, 1), (100, 0)],
            ["ccw_slow", (0, 0), (100, 1), (200, 0)],
            ["ccw_fast", (100, 0), (200, 1)],
        ]
        pv_list_second = [
            ["cw", (-200, 1), (-100, 0)],
            ["stop_pv", (-100, 0), (0, 1), (100, 0)],
            ["ccw", (100, 0), (200, 1)],
        ]
        pv_fuzzy = {}
        for mood in pv_list:
            pv_fuzzy[mood[0]] = self.make_line_equation(mood[1:], x)
        return pv_fuzzy

    def fuzzify_cp(self, x):
        cp_list = [
            ["left_far", (-10, 1), (-5, 0)],
            ["left_near", (-10, 0), (-2.5, 1), (0, 0)],
            ["stop", (-2.5, 0), (0, 1), (2.5, 0)],
            ["right_near", (0, 0), (2.5, 1), (10, 0)],
            ["right_far", (5, 0), (10, 1)]
        ]
        cp_fuzzy = {}
        for mood in cp_list:
            cp_fuzzy[mood[0]] = self.make_line_equation(mood[1:], x)
        return cp_fuzzy

    def fuzzify_cv(self, x):
        cv_list = [
            ["left_fast", (-5, 1), (-2.5, 0)],
            ["left_slow", (-5, 0), (-1, 1), (0, 0)],
            ["stop", (-1, 0), (0, 1), (1, 0)],
            ["right_slow", (0, 0), (1, 1), (5, 0)],
            ["right_fast", (2.5, 0), (5, 1)]
        ]
        cv_fuzzy = {}
        for mood in cv_list:
            cv_fuzzy[mood[0]] = self.make_line_equation(mood[1:], x)
        return cv_fuzzy

    def fuzzify_step(self, input):
        if input['pa'] < 0:
            input['pa'] = 360 + input['pa']
        if input['pv'] > 200:
            input['pv'] = 200
        if input['pv'] < -200:
            input['pv'] = -200
        if input['cp'] > 10:
            input['cp'] = 10
        if input['cp'] < -10:
            input['cp'] = -10
        if input['cv'] > 5:
            input['cv'] = 5
        if input['cv'] < -5:
            input['cv'] = -5
        fuzzification_output = {'pa': self.fuzzify_pa(input['pa']), 'pv': self.fuzzify_pv(input['pv']),
                                'cp': self.fuzzify_cp(input['cp']), 'cv': self.fuzzify_cv(input['cv'])}
        return fuzzification_output

    def inference_step(self, fuzzify_output, extra):
        rules_first = [
            ['pa', 'up', 'pv', 'stop_pv', 'f', 'stop'],
            ['pa', 'up_right', 'pv', 'ccw_slow', 'f', 'stop'],
            ['pa', 'up_left', 'pv', 'cw_slow', 'f', 'stop'],
            ['pa', 'up_more_right', 'pv', 'ccw_slow', 'f', 'right_fast'],
            ['pa', 'up_more_right', 'pv', 'cw_slow', 'f', 'right_fast'],
            ['pa', 'up_more_left', 'pv', 'cw_slow', 'f', 'left_fast'],
            ['pa', 'up_more_left', 'pv', 'ccw_slow', 'f', 'left_fast'],
            ['pa', 'up_more_right', 'pv', 'ccw_fast', 'f', 'left_slow'],
            ['pa', 'up_more_right', 'pv', 'cw_fast', 'f', 'right_fast'],
            ['pa', 'up_more_left', 'pv', 'cw_fast', 'f', 'right_slow'],
            ['pa', 'up_more_left', 'pv', 'ccw_fast', 'f', 'left_fast'],
            ['pa', 'down_more_right', 'pv', 'ccw_slow', 'f', 'right_fast'],
            ['pa', 'down_more_right', 'pv', 'cw_slow', 'f', 'stop'],
            ['pa', 'down_more_left', 'pv', 'cw_slow', 'f', 'left_fast'],
            ['pa', 'down_more_left', 'pv', 'ccw_slow', 'f', 'stop'],
            ['pa', 'down_more_right', 'pv', 'ccw_fast', 'f', 'stop'],
            ['pa', 'down_more_right', 'pv', 'cw_fast', 'f', 'stop'],
            ['pa', 'down_more_left', 'pv', 'cw_fast', 'f', 'stop'],
            ['pa', 'down_more_left', 'pv', 'ccw_fast', 'f', 'stop'],
            ['pa', 'down_right', 'pv', 'ccw_slow', 'f', 'right_fast'],
            ['pa', 'down_right', 'pv', 'cw_slow', 'f', 'right_fast'],
            ['pa', 'down_left', 'pv', 'cw_slow', 'f', 'left_fast'],
            ['pa', 'down_left', 'pv', 'ccw_slow', 'f', 'left_fast'],
            ['pa', 'down_right', 'pv', 'ccw_fast', 'f', 'stop'],
            ['pa', 'down_right', 'pv', 'cw_fast', 'f', 'right_slow'],
            ['pa', 'down_left', 'pv', 'cw_fast', 'f', 'stop'],
            ['pa', 'down_left', 'pv', 'ccw_fast', 'f', 'left_slow'],
            ['pa', 'up_right', 'pv', 'ccw_slow', 'f', 'right_slow'],
            ['pa', 'up_right', 'pv', 'cw_slow', 'f', 'right_fast'],
            ['pa', 'up_right', 'pv', 'stop_pv', 'f', 'right_fast'],
            ['pa', 'up_left', 'pv', 'cw_slow', 'f', 'left_slow'],
            ['pa', 'up_left', 'pv', 'ccw_slow', 'f', 'left_fast'],
            ['pa', 'up_left', 'pv', 'stop_pv', 'f', 'left_fast'],
            ['pa', 'up_right', 'pv', 'ccw_fast', 'f', 'left_fast'],
            ['pa', 'up_right', 'pv', 'cw_fast', 'f', 'right_fast'],
            ['pa', 'up_left', 'pv', 'cw_fast', 'f', 'right_fast'],
            ['pa', 'up_left', 'pv', 'ccw_fast', 'f', 'left_fast'],
            ['pa', 'down', 'pv', 'stop_pv', 'f', 'right_fast'],
            ['pa', 'down', 'pv', 'cw_fast', 'f', 'stop'],
            ['pa', 'down', 'pv', 'ccw_fast', 'f', 'stop'],
            ['pa', 'up', 'pv', 'ccw_slow', 'f', 'left_slow'],
            ['pa', 'up', 'pv', 'ccw_fast', 'f', 'left_fast'],
            ['pa', 'up', 'pv', 'cw_slow', 'f', 'right_slow'],
            ['pa', 'up', 'pv', 'cw_fast', 'f', 'right_fast'],
            ['pa', 'up', 'pv', 'stop_pv', 'f', 'stop']
        ]
        rules_second = [
            ['pa', 'up', 'pv', 'stop_pv', 'f', 'stop'],
            ['pa', 'up_right', 'pv', 'ccw_slow', 'f', 'stop'],
            ['pa', 'up_left', 'pv', 'cw_slow', 'f', 'stop'],
            ['pa', 'up_more_right', 'pv', 'ccw_slow', 'f', 'right_fast'],
            ['pa', 'up_more_right', 'pv', 'cw_slow', 'f', 'right_fast'],
            ['pa', 'up_more_left', 'pv', 'cw_slow', 'f', 'left_fast'],
            ['pa', 'up_more_left', 'pv', 'ccw_slow', 'f', 'left_fast'],
            ['pa', 'up_more_right', 'pv', 'ccw_fast', 'f', 'left_slow'],
            ['pa', 'up_more_right', 'pv', 'cw_fast', 'f', 'right_fast'],
            ['pa', 'up_more_left', 'pv', 'cw_fast', 'f', 'right_slow'],
            ['pa', 'up_more_left', 'pv', 'ccw_fast', 'f', 'left_fast'],
            ['pa', 'down_more_right', 'pv', 'ccw_slow', 'f', 'right_fast'],
            ['pa', 'down_more_right', 'pv', 'cw_slow', 'f', 'stop'],
            ['pa', 'down_more_left', 'pv', 'cw_slow', 'f', 'left_fast'],
            ['pa', 'down_more_left', 'pv', 'ccw_slow', 'f', 'stop'],
            ['pa', 'down_more_right', 'pv', 'ccw_fast', 'f', 'stop'],
            ['pa', 'down_more_right', 'pv', 'cw_fast', 'f', 'stop'],
            ['pa', 'down_more_left', 'pv', 'cw_fast', 'f', 'stop'],
            ['pa', 'down_more_left', 'pv', 'ccw_fast', 'f', 'stop'],
            ['pa', 'down_right', 'pv', 'ccw_slow', 'f', 'right_fast'],
            ['pa', 'down_right', 'pv', 'cw_slow', 'f', 'right_fast'],
            ['pa', 'down_left', 'pv', 'cw_slow', 'f', 'left_fast'],
            ['pa', 'down_left', 'pv', 'ccw_slow', 'f', 'left_fast'],
            ['pa', 'down_right', 'pv', 'ccw_fast', 'f', 'stop'],
            ['pa', 'down_right', 'pv', 'cw_fast', 'f', 'right_slow'],
            ['pa', 'down_left', 'pv', 'cw_fast', 'f', 'stop'],
            ['pa', 'down_left', 'pv', 'ccw_fast', 'f', 'left_slow'],
            ['pa', 'up_right', 'pv', 'ccw_slow', 'f', 'right_slow'],
            ['pa', 'up_right', 'pv', 'cw_slow', 'f', 'right_fast'],
            ['pa', 'up_right', 'pv', 'stop_pv', 'f', 'right_fast'],
            ['pa', 'up_left', 'pv', 'cw_slow', 'f', 'left_slow'],
            ['pa', 'up_left', 'pv', 'ccw_slow', 'f', 'left_fast'],
            ['pa', 'up_left', 'pv', 'stop_pv', 'f', 'left_fast'],
            ['pa', 'up_right', 'pv', 'ccw_fast', 'f', 'left_fast'],
            ['pa', 'up_right', 'pv', 'cw_fast', 'f', 'right_fast'],
            ['pa', 'up_left', 'pv', 'cw_fast', 'f', 'right_fast'],
            ['pa', 'up_left', 'pv', 'ccw_fast', 'f', 'left_fast'],
            ['pa', 'down', 'pv', 'stop_pv', 'f', 'right_fast'],
            ['pa', 'down', 'pv', 'cw_fast', 'f', 'stop'],
            ['pa', 'down', 'pv', 'ccw_fast', 'f', 'stop'],
            ['pa', 'up', 'pv', 'ccw_slow', 'f', 'left_slow'],
            ['pa', 'up', 'pv', 'ccw_fast', 'f', 'left_fast'],
            ['pa', 'up', 'pv', 'cw_slow', 'f', 'right_slow'],
            ['pa', 'up', 'pv', 'cw_fast', 'f', 'right_fast'],
            ['cp', 'left_far', 'cv', 'stop', 'f', 'right_slow'],
            ['cp', 'left_far', 'cv', 'right_fast', 'f', 'stop'],
            ['cp', 'right_far', 'cv', 'stop', 'f', 'left_slow'],
            ['cp', 'right_far', 'cv', 'left_fast', 'f', 'stop'],
            ['cp', 'left_far', 'cv', 'left_fast', 'f', 'right_fast'],
            ['cp', 'left_far', 'cv', 'left_slow', 'f', 'right_slow'],
            ['cp', 'right_far', 'cv', 'right_slow', 'f', 'left_slow'],
            ['cp', 'right_far', 'cv', 'right_fast', 'f', 'left_fast'],
            ['cp', 'right_far', 'cv', 'left_slow', 'f', 'stop'],
            ['cp', 'left_far', 'cv', 'right_slow', 'f', 'stop'],
            ['cp', 'left_near', 'cv', 'left_fast', 'f', 'right_slow'],
            ['cp', 'right_near', 'cv', 'right_fast', 'f', 'left_slow'],
        ]
        if not extra:
            rules = rules_first
        else:
            rules = rules_second
        f = {}
        print(fuzzify_output['pa'],fuzzify_output['pv'])
        for rule in rules:
            number_of_params = (len(rule) - 2) / 2
            value_list = []
            j = 0
            for i in range(number_of_params):
                value_list.append(fuzzify_output[rule[j]][rule[j + 1]])
                j += 2
            if f.get(rule[-1]) is None:
                f[rule[-1]] = min(value_list)
            else:
                if f[rule[-1]] < min(value_list):
                    f[rule[-1]] = min(value_list)
        return f

    def defuzzify_step(self, inference_output):
        print(inference_output)
        f_list = [
            ["left_fast", (-100, 0), (-80, 1), (-60, 0)],
            ["left_slow", (-80, 0), (-60, 1), (0, 0)],
            ["stop", (-60, 0), (0, 1), (60, 0)],
            ["right_slow", (0, 0), (60, 1), (80, 0)],
            ["right_fast", (60, 0), (80, 1), (100, 0)],
        ]
        point = -100
        end = 100
        dx = 0.1
        sum_of_integral = 0
        sum_of_membership = 0
        while point < end:
            temp_list = []
            for mood in f_list:
                temp_list.append(self.make_line_equation(mood[1:], point, max=inference_output[mood[0]]))
            temp = max(temp_list)
            sum_of_integral += temp * point * dx
            sum_of_membership += temp * dx
            point += dx
        if sum_of_membership == 0:
            sum_of_membership += 1
        return sum_of_integral / sum_of_membership

    def setup_model(self, input_world, extra):
        fuzzy_output = self.fuzzify_step(input_world)
        inference_output = self.inference_step(fuzzy_output, extra)
        defuzzication_output = self.defuzzify_step(inference_output)
        return defuzzication_output

    def decide(self, world):
        extra = True
        if not extra:
            coefficient = 1
        else:
            coefficient = 1.75
        output = self._make_output()
        input = self._make_input(world)
        print(input)
        output['force'] = coefficient * self.setup_model(input, extra)
        # self.system.calculate(self._make_input(world), output)
        return output['force']