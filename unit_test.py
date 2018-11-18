#! encoding = utf-8

''' unit tests '''

from data import yyslib, yysdata
import unittest
import numpy as np

import win_unicode_console
win_unicode_console.enable()


class TestConstraintGen(unittest.TestCase):
    ''' test constraint matrix generator
        测试约束矩阵生成器
    '''

    def test(self):

        test_creep_list = ['天邪鬼赤', '独眼小僧', '椒图', '灯笼鬼']

        test_level_list = ['御魂第1层',
                            '探索副本第1章：天邪鬼绿1',
                            '探索副本第1章：天邪鬼绿2',
                            '探索副本第1章：首领',
                            '河畔童谣第8层']

        test_creep_in_level_dict = {
            '御魂第1层': [('天邪鬼赤', 2), ('独眼小僧', 1)],
            '探索副本第1章：天邪鬼绿1': [('天邪鬼赤', 2)],
            '探索副本第1章：天邪鬼绿2': [('天邪鬼绿', 1), ('灯笼鬼', 2)],
            '探索副本第1章：首领': [('灯笼鬼', 3)],
            '河畔童谣第8层': [('椒图', 2)]
        }

        test_out = np.array([[2, 2, 0, 0, 0],
                             [1, 0, 0, 0, 0],
                             [0, 0, 0, 0, 2],
                             [0, 0, 2, 3, 0]
                            ])

        print('\n test constraint matrix function')

        self.assertEqual(True, np.array_equal(test_out, yysdata.gen_complete_constraint(test_creep_list, test_level_list, test_creep_in_level_dict)))



class TestStaminaGen(unittest.TestCase):
    ''' 测试体力向量生成器 '''

    def test(self):

        test_level_list = ['探索副本第1章：首领', '御魂副本第1层', '河畔童谣第8层', '妖气封印：二口女']
        test_single_stanima = [3, 6, 3, 3]
        test_team_stanima = [3, 4, 3, 3]

        print('\n test stamina vector function ')
        self.assertEqual(test_single_stanima,
                         yyslib.gen_stamina(test_level_list, False))
        self.assertEqual(test_team_stanima,
                         yyslib.gen_stamina(test_level_list, True))


class TestTaskStar(unittest.TestCase):
    ''' 测试任务星级分配器 '''

    def test(self):

        test_in = [3, 3, 5, 2, 1, 3]
        test_out = {5: [2], 3: [2, 5, 1, 0], 2: [2, 5, 1, 0, 3],
                            1: [2, 5, 1, 0, 3, 4]}

        print("\n test task star ladder ")
        self.assertEqual(test_out, yyslib.sort_task_star(test_in))


class TestLevelBan(unittest.TestCase):
    ''' 测试副本层数过滤器 '''

    def test(self):

        test_in_1 = [[1], {'yhLevel':(0, 0), 'mwLevel':(0, 0), 'isTeam': True}]
        test_in_2 = [[1], {'yhLevel':(2, 7), 'mwLevel':(1, 10), 'isTeam': True}]

        test_out_1 = [1] + list(range(188, 348))
        test_out_2 = [1, 188, 195, 196, 197]

        print('\n test level id ban')
        self.assertEqual(test_out_1, yyslib.ban_level(test_in_1[0], test_in_1[1]))
        self.assertEqual(test_out_2, yyslib.ban_level(test_in_2[0], test_in_2[1]))


if __name__ == '__main__':
    unittest.main()
