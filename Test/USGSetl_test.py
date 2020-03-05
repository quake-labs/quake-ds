import unittest
from QuakeAPI.USGSetl import *


class USGSetl_Test(unittest.TestCase):
    def test_insert(self):
        fake_quakes = [{"Oceanic": False,
                        "magnitude": 12, "longitude": 0,
                        "latitude": 0, "place": "Null Island",
                        "time": 10}]
        insert_quakes(fake_quakes, "hour")
        check = query_all("SELECT * FROM USGS WHERRE time=10")
        self.assertEqual(set(check[0][1:]), set(fake_quakes[0].values()))
        query_all("delete from USGS where time=10")

    def test_get_time(self):
        times = get_last_times(1582761731160, 'HOUR')
        static_time = [1582758264000, 1582758263830, 1582759368500,
                       1582759486630, 1582759368510, 1582759918440,
                       1582760961770, 1582760961780, 1582761179520,
                       1582761165689, 1582761179530, 1582761165768,
                       1582761712010, 1582761731160, 1582759889310,
                       1582761026296, 1582762288750]
        for time, static in zip(times, static_time):
            self.assertEqual(time, static)


if __name__ == "__main__":
    unittest.main()
