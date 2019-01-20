import unittest

import src.DataManager as dm
import src.Utils as Utils

TESTING_ON = Utils.DATASET_NAME_SMALL

class Tests(unittest.TestCase):
    f = dm.DataManager(TESTING_ON, True)

    datadicts = f._data_dicts
    dataframes = f.get_dataframes()
    idword_dataword_mapping = f._idword_dataword_mapping

    def test_timed_points_in_dataframe(self):
        for label in [Utils.MOVEMENT_POINTS, Utils.TOUCH_DOWN_POINTS, Utils.TOUCH_UP_POINTS]:
            dataframe = self.dataframes[label]
            counter = 0
            for word_id, json_data in self.idword_dataword_mapping.items():
                for point in json_data[label]:
                    self.assertTrue(dataframe.at[counter, Utils.WORD_ID] == word_id)
                    for field in Utils.TIMED_POINTS:
                        self.assertTrue(point[field] == dataframe.at[counter, field])
                    counter += 1
            print("Checked {} {}".format(counter, label))

    def test_untimed_points_in_dataframe(self):
        for label in [Utils.SAMPLED_POINTS]:
            counter = 0
            for word_id, json_data in self.idword_dataword_mapping.items():
                dataframe = self.dataframes[label]
                for current_component, list_of_points in enumerate(json_data[label]):
                    for point in list_of_points:
                        self.assertTrue(dataframe.at[counter, Utils.WORD_ID] == word_id)
                        for field in Utils.POINTS:
                            if field == Utils.COMPONENT:
                                self.assertTrue(current_component == dataframe.at[counter, field])
                            else:
                                self.assertTrue(point[field] == dataframe.at[counter, field])
                        counter += 1
            print("Checked {} {}".format(counter, label))

    def test_dataframes_lenght(self):
        # number of points
        len_fun = lambda label: sum(len(word[label]) for word in self.f._jsons_data)
        number = {
            Utils.MOVEMENT_POINTS: len_fun(Utils.MOVEMENT_POINTS),
            Utils.TOUCH_UP_POINTS: len_fun(Utils.TOUCH_UP_POINTS),
            Utils.TOUCH_DOWN_POINTS: len_fun(Utils.TOUCH_DOWN_POINTS),
            Utils.SAMPLED_POINTS: sum(len(component) for word in self.f._jsons_data for component in word[Utils.SAMPLED_POINTS])
        }
        for label in Utils.POINTS_SERIES_TYPE:
            if label in number:
                self.assertTrue(number[label] == len(self.dataframes[label]))
        self.assertTrue(number[Utils.TOUCH_DOWN_POINTS] == number[Utils.TOUCH_UP_POINTS])

        # number of words
        aspected_number_of_words = sum(x[Utils.TOTAL_WORD_NUMBER] for x in self.datadicts[Utils.USERID_USERDATA].values())
        number_word = len(self.f._jsons_data)
        self.assertTrue(aspected_number_of_words == number_word ==
                        len(self.idword_dataword_mapping) == len(self.datadicts[Utils.WORDID_USERID]))

        # check that the words have the same ids
        self.assertTrue(set(self.datadicts[Utils.WORDID_USERID].keys()) == set(self.idword_dataword_mapping.keys()))

        # number of user
        self.assertTrue(set(self.datadicts[Utils.USERID_USERDATA].keys()) == set(self.datadicts[Utils.WORDID_USERID].values()))

    def test_dataframes_pickle_saving(self):
        dm.DataManager(TESTING_ON, update_data=True)._save_dataframes()
        for (l, read_value), (_, gen_value) in zip(sorted(dm.DataManager(TESTING_ON, update_data=False).get_dataframes().items()),
                                                   sorted(dm.DataManager(TESTING_ON, update_data=True).get_dataframes().items())):
            self.assertTrue(read_value.equals(gen_value))


if __name__ == '__main__':
    unittest.main()
