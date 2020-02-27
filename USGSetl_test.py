import unittest

from QuakeAPI.USGSetl import *

class USGSetl_Test(unittest.TestCase):
    def test_insert(self):
        fake_quakes = [{"Oceanic":False,
                        "magnitude":12, "longitude":0,
                        "latitude":0, "place":"Null Island",
                        "time":10}]
        insert_quakes(fake_quakes, "hour")
        check = query_all("select * from USGS where time=10")
        self.assertEqual (set(check[0][1:]),set(fake_quakes[0].values()))
        query_all ("delete from USGS where time=10")

    def test_get_recent(self):
        recent = get_recent_quakes('https://quake-ds-production.herokuapp.com/test')
        self.assertEqual(list(recent[0].values()),
                        [3,"5km WNW of Cobb, CA",
                        1582252014390,-122.776001,38.8348351,0.4,false])


if __name__ == "__main__":
    unittest.main()
