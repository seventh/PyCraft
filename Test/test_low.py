# -*- coding: utf-8 -*-

"""Check low-level binary readers/writers
"""

import unittest
from io import BytesIO
from collections import namedtuple

from pycraft.low import *


ScenarioStep = namedtuple("ScenarioStep", "read, write, value")


class LowTest(unittest.TestCase):

    def run_scenario(self, scenario):
        # First, write all the data
        flow = BytesIO()
        for step in scenario:
            step.write(flow, step.value)

        # Then, read it and check it wasn't degraded
        flow.seek(0, 0)
        for step in scenario:
            try:
                value = step.read(flow, len(step.value))
            except TypeError:
                value = step.read(flow)
            self.assertEqual(step.value, value)

    def test_byte(self):
        scenario = [ScenarioStep(read_byte, write_byte, 30),
                    ScenarioStep(read_byte, write_byte, (2, 120, 235))]

        self.run_scenario(scenario)

    def test_short(self):
        scenario = [ScenarioStep(read_short, write_short, 30),
                    ScenarioStep(read_short, write_short, (2, -120, 35))]

        self.run_scenario(scenario)

    def test_int(self):
        scenario = [ScenarioStep(read_int, write_int, 30),
                    ScenarioStep(read_int, write_int, (2, -120, 35))]

        self.run_scenario(scenario)

    def test_long(self):
        scenario = [ScenarioStep(read_long, write_long, 30),
                    ScenarioStep(read_long, write_long, (2, -120, 35))]

        self.run_scenario(scenario)

    def test_float(self):
        scenario = [ScenarioStep(read_float, write_float, 30.125),
                    ScenarioStep(read_float, write_float, (2.5, -120, 35.75))]

        self.run_scenario(scenario)

    def test_double(self):
        scenario = [ScenarioStep(read_double, write_double, 30),
                    ScenarioStep(read_double, write_double, (2, -120, 35))]

        self.run_scenario(scenario)

    def test_byte_array(self):
        scenario = [ScenarioStep(read_byte_array, write_byte_array, [255]),
                    ScenarioStep(read_byte_array, write_byte_array,
                                 [0, 42, 127])]

        self.run_scenario(scenario)

    def test_string(self):
        scenario = [ScenarioStep(read_string, write_string,
                                 b"carr\xc3\xa9ment m\xc3\xa9chant, jamais \xc3\xa0 c\xc5\x93ur".decode("utf-8")),
                    ScenarioStep(read_string, write_string,
                                 b"dans ton \xc5\x93il".decode("utf-8"))]

        self.run_scenario(scenario)

    def test_int_array(self):
        scenario = [ScenarioStep(read_int_array, write_int_array, [-128]),
                    ScenarioStep(read_int_array, write_int_array,
                                 [42, -128, 127])]

        self.run_scenario(scenario)


if __name__ == "__main__":
    unittest.main()
