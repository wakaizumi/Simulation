#シミュレーションに関わる関数

import numpy as np
import random
from def1 import *

def a_star(field,start_node,end_node,a_star_type = 0, remove_node_list = []):
    G = field.G

    if start_node == end_node: return
    f_cost = {x:float('inf') for x in G.nodes()} #fコスト
    g_cost = {x:float('inf') for x in G.nodes()} #gコスト
    P = {x:None for x in G.nodes()} #親ノード
    frontier = set({})
    explored = set({})
    f_cost[start_node] = 0
    g_cost[start_node] = 0
    frontier.add(start_node)
    while True:
        f_min = float('inf')
        n = None
        for i in frontier:
            if f_cost[i] < f_min:
                f_min = f_cost[i]
                n = i

        if n == end_node:break
        #ゴールにつく前に探索できる場所がなくなったとき
        if n == None:
            return None,None,None,None
        frontier.discard(n)
        explored.add(n)

        for (x,nc) in G.edges(n):
            #index = link_index[n,nc]
            index = node_to_link_index(field.node_df,field.link_df,n,nc)
            v = field.speed[index] if a_star_type == 1 else 1.2
            if nc in explored:continue
            if nc in frontier and g_cost[nc] <= g_cost[n] + round(weight_get(field.node_df,field.link_df,n,nc) / v,1):continue
            frontier.add(nc)
            if nc in remove_node_list:
                g_cost[nc] = float('inf')
                f_cost[nc] = float('inf')
                frontier.discard(nc)
                explored.add(nc)
                continue
            P[nc] = n
            g_cost[nc] = g_cost[n] + round(weight_get(field.node_df,field.link_df,n,nc) / v,1)
            f_cost[nc] = g_cost[nc] + round(round(google_distance(field.node_df.lat[nc],field.node_df.lon[nc],
                                                      field.node_df.lat[end_node],field.node_df.lon[end_node]),1) / 1.2,1)

    next_node,next_link,start_link,use_link_index = path_generator_astar(field,P,end_node)
    return next_node,next_link,start_link,use_link_index
    
def a_star_dens(field,start_node,end_node,remove_node_list = []):
    
    if start_node == end_node: return None,None,None,None
    
    def f_speed_dens(x):return max(1.356 - 5.424 * x, 0)
    
    G = field.G
    f_cost = {x:float('inf') for x in G.nodes()} #fコスト
    g_cost = {x:float('inf') for x in G.nodes()} #gコスト
    f_cost[start_node] = 0
    g_cost[start_node] = 0
    P = {x:None for x in G.nodes()} #親ノード
    frontier = set({})
    explored = set({})
    
    frontier.add(start_node)
    while True:
        f_min = float('inf')
        n = None
        for i in frontier:
            if f_cost[i] < f_min:
                f_min = f_cost[i]
                n = i

        if n == end_node:break
        #ゴールにつく前に探索できる場所がなくなったとき
        if n == None:
            return None,None,None,None
        frontier.discard(n)
        explored.add(n)

        for (x,nc) in G.edges(n):
            #index = link_index[n,nc]
            index = node_to_link_index(field.node_df,field.link_df,n,nc)
            #v = field.speed[index] if a_star_type == 1 else 1.2
            v = f_speed_dens(field.dens[index]) #人口密度考慮版の速度式
            
            #すでに計算終了ノード　または　人口密度が高いリンク
            if nc in explored:continue
            if v == 0:
                explored.add(nc)
                continue

            if nc in frontier and g_cost[nc] <= g_cost[n] + round(weight_get(field.node_df,field.link_df,n,nc) / v,1):continue
            frontier.add(nc)
            if nc in remove_node_list:
                g_cost[nc] = float('inf')
                f_cost[nc] = float('inf')
                frontier.discard(nc)
                explored.add(nc)
                continue
            P[nc] = n
            g_cost[nc] = g_cost[n] + round(weight_get(field.node_df,field.link_df,n,nc) / v,1)
            f_cost[nc] = g_cost[nc] + round(round(google_distance(field.node_df.lat[nc],field.node_df.lon[nc],
                                                      field.node_df.lat[end_node],field.node_df.lon[end_node]),1) / 1.2,1)
    
    next_node,next_link,start_link,use_link_index = path_generator_astar(field,P,end_node)
    return next_node,next_link,start_link,use_link_index

    
def route_num(field):
    s = set()
    for i in range(len(field.agent_list)):
        log_time,log_route = field.agent_list[i].get_log()
        log_route_tuple = tuple(log_route)
        s.add(log_route_tuple)
    return s,len(s)

def path_generator_astar(field,P,end):
    use_link = []
    next_node = {}
    next_link = {}
    i = end
    while P[i] != None:
        next_node[P[i]] = i
        use_link.append((i,P[i]))
        i = P[i]
    #use_link_index = []
    use_link_index = [node_to_link_index(field.node_df,field.link_df,use_link[i][0],use_link[i][1]) for i in range(len(use_link))]
    start_link = use_link_index[-1]

    for i in range(len(use_link_index)):
        if i != 0:next_link[use_link_index[i]] = use_link_index[i-1]
        else:next_link[use_link_index[i]] = None
    return next_node,next_link,start_link,use_link_index

#Pは最小全域木
def path_generator(field,P,start,end):
    use_link = []
    use_link_index = []
    next_node = {}
    next_link = {}
    start_link = 0
    i = start
    while i != end:
        next_node[i] = P[i]
        use_link_index.append(node_to_link_index(field.node_df,field.link_df,i,P[i]))
        i = P[i]
    if len(use_link_index)!=0:start_link = use_link_index[0]

    for i,v in enumerate(use_link_index):
        if i != len(use_link_index)-1: next_link[v] = use_link_index[i+1]
        else: next_link[v] = None
    return next_node,next_link,start_link,use_link_index

def shortest_path(field,start,end):
    P = pickle_load('/home/wakaizumi/program/M1/道路ネットワーク/pickle/route/route_{}.pickle'.format(end))#既に保存済み
    next_node,next_link,start_link,use_link_index = path_generator(field,P,start,end)
    return next_node,next_link,start_link,use_link_index

def distance_calc(field,pos,end):
    D = pickle_load('/home/wakaizumi/program/M1/道路ネットワーク/pickle/distance/distance_{}.pickle'.format(end))#既に保存済み
    return D[pos]

def random_route(field,start,end,remove_node_list=[]):
    """
    remove_node_list.append(start)             
    return shortest_path(field,start,end)#経路が見つからなかった
    """
    remove_node_list.append(start)
    for (x,n1) in field.G.edges(start):
        if n1 in remove_node_list:continue
        if n1 == end:return shortest_path(field,start,end)
        for (y,n2) in field.G.edges(n1):
            if n2 in remove_node_list:continue
            if n2 == end:shortest_path(field,start,end)
            next_node,next_link,start_link1,use_link_index = shortest_path(field,n2,end)
            link1 = node_to_link_index(field.node_df,field.link_df,start,n1)
            link2 = node_to_link_index(field.node_df,field.link_df,n1,n2)
            start_link = link1
            use_link_index.append(link1)
            use_link_index.append(link2)
            next_node[start]=n1
            next_node[n1]=n2
            next_link[link1]=link2
            next_link[link2]=start_link1
            return next_node,next_link,start_link,use_link_index                     
    return shortest_path(field,start,end)#経路が見つからなかった