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


if __name__ == "__main__":
    unittest.main()
