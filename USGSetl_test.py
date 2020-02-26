import unittest

from QuakeAPI.USGSetl import insert_quakes, query_all

class USGSetl_Test(unittest.TestCase):
    def test_insert(self):
        fake_quakes = [{"Oceanic":False, 
                        "magnitude":12, "longitude":0,
                        "latitude":0, "place":"Null Island",
                        "time":10}]
        insert_quakes(fake_quakes)
        check = query_all("select * from USGS where time=10")
        print (check)


if __name__ == "__main__":
    unittest.main()