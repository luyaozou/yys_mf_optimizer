#! encoding = utf-8

''' 阴阳师任务规划器和函数库 '''

import numpy as np
from data import yysdata
import re
import pulp
import pickle


def wrap_all_together(task_entries, ban_opts):
    ''' Get shit together.
    Arguments:
        task_entries -- [('creep_name',
                          <creep_num, int>,
                          <task_star, int>)]
        ban_opts -- {'isBoss': bool, 'isTeam': bool,
                     'yhLevel': <(min, max), int>,
                     'mwLevel': <(min, max), int>}
    Returns:
        full_res -- {task_star: (status, solution, total_s)}
            status -- pulp status: 'Optimal', 'Unbound', 'Unsolvable'
            solution -- [([<'level_name'>, ...], <level_num, float>), ...]
            total_s -- total stamina, int
    '''

    task_creep_list, task_creep_num_list, task_star_list = parse_task(task_entries)

    # 分配任务星级
    task_ladder = sort_task_star(task_star_list)
    # full result
    full_res = {}
    for key, index in task_ladder.items():
        this_task_creep_list = [task_creep_list[i] for i in index]
        this_task_creep_num_list = [task_creep_num_list[i] for i in index]
        full_res[key] = solve_single_prob(this_task_creep_list, this_task_creep_num_list, ban_opts)

    return full_res


def solve_single_prob(task_creep_list, task_creep_num_list, ban_opts):
    ''' solve singel problem.
    Arguments:
        task_creep_list -- [<'creep-name'>]
        task_creep_num_list -- [<creep_num, int>]
        ban_opts -- {'opt-name': <value, bool/int>}
    Returns:
        status -- pulp status: 'Optimal', 'Unbound', 'Unsolvable'
        solution -- [([<'level_name'>, ...], <level_num, float>), ...]
        total_s -- total stamina, float
    '''

    # 限定御魂和秘闻副本层数
    creep_id = task_creep_id(task_creep_list)
    banned_level_id = ban_level(ban_opts)
    sub_c, level_id = gen_sub_constraint(creep_id, banned_level_id)

    # solve the prob
    status, solution, total_s = lp_opt(sub_c, task_creep_num_list, level_id, isTeam=ban_opts['isTeam'], isBoss=ban_opts['isBoss'])

    return status, solution, total_s


def sort_task_star(task_star_list):
    ''' Sort task_star. 按任务星级从高到低分阶梯返回
    Returns:
        task_ladder -- {task_star, int: [task_list_index, int]}
    '''

    task_ladder = {}

    idx = sorted(range(len(task_star_list)), key = lambda k: task_star_list[k])
    sorted_task_star = [task_star_list[i] for i in idx]

    # pop the last sorted item, i.e., the highest star
    a = sorted_task_star.pop()
    a_idx = idx.pop()
    # put it into the ladder dict
    task_ladder[a] = [a_idx]
    # if there are still tasks left
    while sorted_task_star:
        # pop the highest star in the remaining of the task list
        b = sorted_task_star.pop()
        b_idx = idx.pop()
        if a == b:
            # if a & b are equal, append the index to the ladder dict
            task_ladder[a].append(b_idx)
        else:
            # if a > b, create a new ladder key
            task_ladder[b] = task_ladder[a].copy()
            task_ladder[b].append(b_idx)
        a = b   # replace a with b (which becomes the new a)

    return task_ladder


def parse_task(task_list):
    ''' parse task list '''

    task_creep_list = []
    task_creep_num_list = []
    task_star_list = []

    for task in task_list:
        (creep_name, creep_num, task_star) = task
        task_creep_list.append(creep_name)
        task_creep_num_list.append(creep_num)
        task_star_list.append(task_star)

    return task_creep_list, task_creep_num_list, task_star_list


def task_creep_id(task_creep_list):
    ''' 生成任务妖怪在妖怪库中的索引号
    Returns
        creep_id -- [int]
    '''

    creep_id = []
    for creep in task_creep_list:
        creep_id.append(yysdata.CREEP_LIST.index(creep))

    return creep_id


def gen_sub_constraint(creep_id, banned_level_id):
    ''' 生成任务妖怪对应的子约束矩阵。
        去掉全0行&全0列，以及 banned_level_id 的限定列
    Returns:
        sub_c -- np.array()
        col_id -- non-zero column id, list
    '''

    # first, get only rows corresponding to creep_id
    _temp_c = COMPLETE_C[creep_id, :]
    # second, return non-zero column ids,
    # and then remove all zero columns
    # need to determine if _temp_c is only a vector, i.e. len(creep_id)=1

    non_zero_cols = []

    if len(_temp_c.shape) == 1:
        # non-zero terms
        col_id = np.nonzero(_temp_c)[0].tolist()
        # substract banned levels
        for id in banned_level_id:
            if id in col_id:
                col_id.remove(id)
            else:
                pass
        return _temp_c[col_id], col_id
    else:
        for col in range(_temp_c.shape[1]):
            if _temp_c[:, col].any() and col not in banned_level_id:
                non_zero_cols.append(col)
            else:
                pass
        return _temp_c[:, non_zero_cols], non_zero_cols


def ban_level(ban_opts):
    ''' 返回 ban_opts 禁止的关卡层数 id 列表
    Arguments
        ban_opts -- {'opt-name': <value, bool/int>}
    Returns
        level_id, list
    '''

    banned_level_id = []
    yhmin, yhmax = ban_opts['yhLevel']
    mwmin, mwmax = ban_opts['mwLevel']

    for i in range(len(yysdata.LEVEL_NAME_LIST)):
        level = yysdata.LEVEL_NAME_LIST[i]
        if '御魂' in level:
            if not (yhmin or yhmax): # if both are 0
                banned_level_id.append(i)
            else:
                level_num = int(re.search('(\d+)', level).groups()[0])
                if level_num < yhmin or level_num > yhmax:
                    # banned level
                    banned_level_id.append(i)
                else:
                    pass
        elif '妖气' not in level and '探索' not in level :  # 秘闻副本
            if not (mwmin or mwmax): # if both are 0
                banned_level_id.append(i)
            else:
                level_num = int(re.search('(\d+)', level).groups()[0])
                if level_num < mwmin or level_num > mwmax:
                    # banned level
                    banned_level_id.append(i)
                else:
                    pass
        elif '妖气' in level and not ban_opts['isTeam']:     #不组队时不打妖气封印
            banned_level_id.append(i)
        else:
            pass

    if ban_opts['isBoss']:
        pass
    else:
        for id in ALL_BOSS_LEVEL_DICT.keys():
            banned_level_id.append(id)

    return banned_level_id


def gen_stamina(chosen_level_list, isTeam=False):
    ''' 从所选的关卡子列表中生成体力消耗矢量。包含组队选项 '''

    stamina = []

    for level in chosen_level_list:
        if level.find('御魂') == -1:  #非御魂副本
            stamina.append(3)
        else:
            if isTeam:
                stamina.append(4)
            else:
                stamina.append(6)

    return stamina


def lp_opt(c, creep_num, level_id, isTeam=False, isBoss=False):
    ''' 整数线性优化
    Arguments:
        c -- 约束矩阵 c[i][j]
        creep_num -- 约束条件：怪物数量列表
        level_id -- 自变量：关卡 id
        isTeam -- bool, 是否组队
        isBoss -- bool, 是否攻打首领
    Returns:
        prob.status -- pulp status
        solution -- [([<'level_name'>, ...], <level_num, float>), ...]
        total_s -- total stamina, float
    '''

    prob = pulp.LpProblem(name = 'yys_opt', sense=pulp.LpMinimize)

    stamina = gen_stamina([yysdata.LEVEL_NAME_LIST[i] for i in level_id], isTeam)

    # append stamina to the first row of constraint matrix c
    c = np.vstack((stamina, c))
    x = [pulp.LpVariable('x{:d}'.format(i), lowBound=0, cat=pulp.LpInteger) for i in level_id]

    obj = pulp.LpAffineExpression([(x[j], c[0, j]) for j in range(len(level_id))])
    # objective funciton
    prob += pulp.lpSum(obj)
    # normal constraints
    for i in range(len(creep_num)):
        _t = pulp.LpAffineExpression([(x[j], c[i+1, j]) for j in range(len(level_id))])
        prob += pulp.lpSum(_t) >= creep_num[i]
    prob.solve()
    solution = []

    # and this is ABSOLUTELY stupid: believe it or not,
    # the index [i] pulp returns is not equal to the
    # index j of x[level_id] in level_id!
    # pulp shuffles the list!!!
    # therefore, I've gotta get level id from x.name,
    # and store the varValue as well with the right id
    # Let's do it
    x0 = np.zeros(len(level_id))
    for x in prob.variables():
        if x.varValue:  # if non-zero
            j = level_id.index(int(x.name[1:]))
            x0[j] = x.varValue
        else:
            pass
    # remember, j is the col index in c[i][j] & level_id
    # level_id[j] is the level index in the complete LEVEL_NAME_LIST

    # check if boos level is in the result.
    # if so & isBoss = True, redo the optimization with extra constraints
    # 逻辑是，对 boss level, 先调取与其关联的其他层数 id
    # 随后将这些层数分为两类：类 1 已在 sub_c 中，类 2 不在 sub_c 中
    # 对类 1，lowerBound 改为 >= boss level 攻打次数
    # 对类 2, 只计算其个数，并将相应体力值加到 boss level 的体力值上
    if isBoss:
        x0_boss = {}        # {boss_id: ([type_1_j], [type_2])}
        for j in np.nonzero(x0)[0].tolist():
            # search boss level in all nonzero value levels
            if level_id[j] in ALL_BOSS_LEVEL_DICT:
                # found boss level
                type_1_j = []
                type_2 = []
                for id in ALL_BOSS_LEVEL_DICT[level_id[j]]:
                    # get linked creep levels
                    if id in level_id:  # if it is in sub_c
                        type_1_j.append(level_id.index(id))
                    else:
                        type_2.append(id)
                x0_boss[j] = (type_1_j, type_2)
            else:
                pass
        # resolve the problem
        prob = pulp.LpProblem(name = 'yys_opt', sense=pulp.LpMinimize)
        # recreate stamina
        for boss_j in x0_boss:
            c[0, boss_j] = 3 * len(x0_boss[boss_j][1]) + 3
        # recreate variable & constraint
        x = [pulp.LpVariable('x{:d}'.format(i), lowBound=0, cat=pulp.LpInteger) for i in level_id]
        obj = pulp.LpAffineExpression([(x[j], c[0, j]) for j in range(len(level_id))])
        # objective funciton
        prob += pulp.lpSum(obj)
        # adding constraints
        for i in range(len(creep_num)):
            _t = pulp.LpAffineExpression([(x[j], c[i+1, j]) for j in range(len(level_id))])
            prob += pulp.lpSum(_t) >= creep_num[i]
        print('x=', x)
        print('x0_boss=', x0_boss)
        for boss_j in x0_boss:
            for j in x0_boss[boss_j][0]:
                prob += x[j] >= x[boss_j]
        prob.solve()

        x0 = np.zeros(len(level_id))
        for x in prob.variables():
            if x.varValue:  # if non-zero
                j = level_id.index(int(x.name[1:]))
                x0[j] = x.varValue
            else:
                pass
    else:
        pass


    # find identical levels and return all of them in the result
    identical_cols = {}
    for j in np.nonzero(x0)[0].tolist():    # get col id of nonzero x
        cj = c[:, j]
        identical_cols[j] = []
        for k in range(len(x0)):    # find identical cols
            ck = c[:, k]
            if k != j and np.array_equal(cj, ck):
                identical_cols[j].append(k)
            else:
                pass
    for j, ks in identical_cols.items():
        if ks:
            level_names = [yysdata.LEVEL_NAME_LIST[level_id[j]]] + \
                          [yysdata.LEVEL_NAME_LIST[level_id[k]] for k in ks]
        else:
            level_names = [yysdata.LEVEL_NAME_LIST[level_id[j]]]
        level_names.sort()
        solution.append((level_names, x0[j]))
    total_s = np.dot(x0, c[0, :].transpose())

    return prob.status, solution, total_s


def load_data():
    with open('data/d.pkl', 'rb') as f:
        global COMPLETE_C
        COMPLETE_C = pickle.load(f)
        global ALL_BOSS_LEVEL_DICT
        ALL_BOSS_LEVEL_DICT = pickle.load(f)
