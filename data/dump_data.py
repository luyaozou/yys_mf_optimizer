#! encoding = utf-8

''' Dump data to file so that it can be reuse '''

import pickle
import numpy as np
from yysdata import *

def _gen_complete_constraint(creep_list=CREEP_LIST, level_name_list=LEVEL_NAME_LIST, creep_in_level_dict=CREEP_IN_LEVEL):
    ''' 生成完整的约束矩阵 c[i][j], i = 妖怪编号，j = 副本关卡编号，
        c[i][j] 为妖怪数
        creep_list: 妖怪名单
        level_list: 副本关卡名单
        creep_in_level_dict: 每关中妖怪的数量
    '''

    c = np.zeros((len(creep_list), len(level_name_list)))

    for level_key in creep_in_level_dict.keys():
        # key: level name
        # value: (creep_name, creep_num)
        j = level_name_list.index(level_key)
        for value in creep_in_level_dict[level_key]:
            if value[0] in creep_list:      # prevent error
                i = creep_list.index(value[0])
                c[i][j] = value[1]
            else:
                pass

    return c


def _boss_level_id_link(name_list, link_dict):
    ''' 关联首领关卡编号和对应探索副本其他小怪关卡编号
    Returns
        link_id_dict -- {<boss_level_id, int>: [<creep_level_id, int>]}
    '''

    link_id_dict = {}

    for key, value in link_dict.items():
        key_id = name_list.index(key)
        value_id = [name_list.index(v) for v in value]
        link_id_dict[key_id] = value_id

    return link_id_dict


with open('data/d.pkl', 'wb') as f:
    COMPLETE_C = _gen_complete_constraint()
    pickle.dump(COMPLETE_C, f, pickle.DEFAULT_PROTOCOL)
    ALL_BOSS_LEVEL_DICT = _boss_level_id_link(LEVEL_NAME_LIST, BOSS_LEVEL_LINK)
    pickle.dump(ALL_BOSS_LEVEL_DICT, f, pickle.DEFAULT_PROTOCOL)
