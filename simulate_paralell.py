#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import psutil
import os
import numpy as np
import random
import tracemalloc
import concurrent.futures

# 为了加快模拟速度，取消 sleep 延时
time.sleep = lambda x: None

# 导入棋盘和 AI 模块（请确保项目结构正确）
from board import Board
from ai.greedy_ai import GreedyAI
from ai.astar_ai import AStarAI
from ai.mcts_ai import MCTSAI
from ai.minimax_ai import MinimaxAI

def simulate_game_with_stats(max_moves, agents):
    """
    模拟一局游戏：
      - max_moves: 最大走子步数（例如 1 分钟 = 60 步）
      - agents: 字典 {1: agent1, 2: agent2, 3: agent3, 4: agent4}
    当游戏结束或达到最大步数后，根据各玩家目标区域内的棋子数确定胜者，
    如果所有玩家得分都为 0，则返回 winner=0 表示平局。
    同时记录每步决策的耗时和内存峰值。
    
    返回字典：
      {
         'winner': 获胜玩家ID or 0,
         'moves': 实际走步数,
         'stats': { p: {'times': [每步时间], 'mems': [每步内存] } }
      }
    """
    board_instance = Board()  # 初始棋盘，要求初始布局采用对角起始（目标区域为空）
    current_player = 1
    moves_count = 0
    process = psutil.Process(os.getpid())
    
    # 初始化每个玩家决策统计数据
    stats = {
        1: {'times': [], 'mems': []},
        2: {'times': [], 'mems': []},
        3: {'times': [], 'mems': []},
        4: {'times': [], 'mems': []}
    }
    
    while moves_count < max_moves and not board_instance.is_game_over():
        agent = agents[current_player]
        tracemalloc.start()
        start_time = time.time()
        move = agent.choose_move(board_instance.board)
        step_time = time.time() - start_time
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        stats[current_player]['times'].append(step_time)
        stats[current_player]['mems'].append(peak)
        
        if move:
            from_pos, to_pos = move
            board_instance.move_piece(from_pos, to_pos)
        moves_count += 1
        current_player = (current_player % 4) + 1

    board_arr = board_instance.board
    # 统计目标区域得分
    p1_score = np.count_nonzero(board_arr[9:12, 9:12] == 1)  # 玩家1目标区域：右下
    p2_score = np.count_nonzero(board_arr[9:12, 0:3] == 2)     # 玩家2目标区域：左下
    p3_score = np.count_nonzero(board_arr[0:3, 9:12] == 3)     # 玩家3目标区域：右上
    p4_score = np.count_nonzero(board_arr[0:3, 0:3] == 4)      # 玩家4目标区域：左上
    scores = {1: p1_score, 2: p2_score, 3: p3_score, 4: p4_score}
    # 如果所有得分均为 0，则返回平局 winner = 0
    if all(score == 0 for score in scores.values()):
        winner = 0
    else:
        winner = max(scores, key=scores.get)
    
    return {'winner': winner, 'moves': moves_count, 'stats': stats}

def simulate_battles(time_limit_minutes, rounds=10):
    """
    针对指定时长（分钟），进行 rounds 局模拟。
    时长以走子步数表示（分钟 * 60）。
    使用多进程并行执行各局模拟以加快速度。
    
    返回统计数据：包括每个玩家的胜局数、胜率、平均每步决策时间和平均每步内存使用（单位字节）。
    """
    max_moves = time_limit_minutes * 60
    print(f"\n开始模拟：游戏时长 {time_limit_minutes} 分钟（最多走 {max_moves} 步），共 {rounds} 盘。")
    # 固定 Agent 分配：玩家1：Greedy，玩家2：A* 算法，玩家3：MCTS，玩家4：Minimax
    agents_template = {
        1: GreedyAI(1),
        2: AStarAI(2),
        3: MCTSAI(3),
        4: MinimaxAI(4)
    }
    
    round_results = []
    # 使用 ProcessPoolExecutor 并行执行各局模拟
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(simulate_game_with_stats, max_moves, agents_template)
            for _ in range(rounds)
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                round_results.append(result)
                if result['winner'] == 0:
                    print(f"局结果: 平局, Moves = {result['moves']}")
                else:
                    print(f"局结果: Winner = {result['winner']}, Moves = {result['moves']}")
            except Exception as e:
                print(f"模拟过程中发生异常：{e}")
    
    win_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    total_times = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
    total_mems = {1: 0, 2: 0, 3: 0, 4: 0}
    total_steps = {1: 0, 2: 0, 3: 0, 4: 0}
    
    for res in round_results:
        if res['winner'] in win_counts:
            win_counts[res['winner']] += 1
        stats = res['stats']
        for p in [1, 2, 3, 4]:
            total_times[p] += sum(stats[p]['times'])
            total_mems[p] += sum(stats[p]['mems'])
            total_steps[p] += len(stats[p]['times'])
    
    avg_times = {p: (total_times[p] / total_steps[p] if total_steps[p] > 0 else 0) for p in [1,2,3,4]}
    avg_mems = {p: (total_mems[p] / total_steps[p] if total_steps[p] > 0 else 0) for p in [1,2,3,4]}
    win_rates = {p: (win_counts[p] / rounds * 100) for p in [1,2,3,4]}
    
    results = {
        'win_counts': win_counts,
        'win_rates': win_rates,
        'avg_times': avg_times,
        'avg_mems': avg_mems
    }
    return results

def print_results_table(time_limit, results):
    print("\n========================================")
    print(f"游戏时长：约 {time_limit} 分钟   (10 盘模拟)")
    print("------------------------------------------------")
    print(f"{'Algorithm':<12}{'Wins':>8}{'Win Rate':>10}{'Avg Time/Step(s)':>20}{'Avg Mem/Step(MB)':>22}")
    print("------------------------------------------------")
    # 固定对应关系：玩家1：Greedy, 玩家2：A* 算法, 玩家3：MCTS, 玩家4：Minimax
    algo_names = {1: "Greedy", 2: "A star", 3: "MCTS", 4: "Minimax"}
    for p in [1,2,3,4]:
        wins = results['win_counts'][p]
        rate = results['win_rates'][p]
        avg_time = results['avg_times'][p]
        avg_mem = results['avg_mems'][p] / (1024*1024)  # 转换为 MB
        print(f"{algo_names[p]:<12}{wins:8d}{rate:9.1f}%{avg_time:20.3f}{avg_mem:22.2f}")
    print("========================================\n")

if __name__ == '__main__':
    # 分别对1、2、3、4、5分钟模拟，每个时长模拟10局
    durations = [1, 2, 3, 4, 5]
    rounds = 10
    for t in durations:
        results = simulate_battles(t, rounds)
        print_results_table(t, results)
