#データフレームの操作系の関数

import numpy as np
import pickle

# リンクindexから両端のノードインデックスを返す関数
def link_node(node_df,link_df,index):
    link_s = link_df.start_id[index]
    link_e = link_df.end_id[index]
    node_s = int(node_df[node_df.node_id==link_s].index.values)
    node_e = int(node_df[node_df.node_id==link_e].index.values)
    return node_s,node_e

#座標からノードインデックスを返す関数
def node_index(node_df,link_df,lat,lon):
    for i in node_df.index:
        if node_df.lat[i] == lat and node_df.lon[i] == lon:
            return i

#両端ノードの組み合わせからリンク番号を導く
#既に辞書を保存しておく　計算時間32s→1.46s
def node_to_link_index(node_df,link_df,node1,node2):
    link_index = pickle_load('/home/wakaizumi/program/M1/道路ネットワーク/pickle/link_index_tokyo.pickle')#既に保存済み
    #link_index = pickle_load('/home/wakaizumi/program/M1/道路ネットワーク/pickle/link_index_yokohama.pickle')
    return link_index[node1,node2]
#保存している辞書がないバージョン
"""
def node_to_link_index(node_df,link_df,node1,node2):
    for index in range(len(link_df)):
        if link_df['node_s'][index] == node1:
            if link_df['node_e'][index] == node2:
                return index
        elif link_df['node_s'][index] == node2:
            if link_df['node_e'][index] == node1:
                return index
"""

#2つの座標からそのリンクの重さを返す関数
def weight_get(node_df,link_df,x,y):
    return link_df.distance[node_to_link_index(node_df,link_df,x,y)]

#googleMapAPI　球面三角法
def google_distance(lat_a,lon_a,lat_b,lon_b):
    r = 6378137.0  #赤道半径
    rad_lat_a=np.radians(lat_a)
    rad_lon_a=np.radians(lon_a)
    rad_lat_b=np.radians(lat_b)
    rad_lon_b=np.radians(lon_b)
    
    averageLat = (rad_lat_a - rad_lat_b) / 2
    averageLon = (rad_lon_a - rad_lon_b) / 2
    
    return r * 2 * np.arcsin(np.sqrt(np.power(np.sin(averageLat), 2) 
                                     + np.cos(rad_lat_a) * np.cos(rad_lat_b) * np.power(np.sin(averageLon),2)))

def wgs84_to_web_mercator(lon, lat):
    """Converts decimal longitude/latitude to Web Mercator format"""
    k = 6378137
    x = lon * (k * np.pi/180.0)
    y = np.log(np.tan((90 + lat) * np.pi/360.0)) * k
    return x, y

def wgs84_to_web_mercator_x(lon):
    """Converts decimal longitude to Web Mercator X"""
    k = 6378137
    x = lon * (k * np.pi/180.0)    
    return x

def wgs84_to_web_mercator_y(lat):
    """Converts decimal latitude to Web Mercator format"""
    k = 6378137    
    y = np.log(np.tan((90 + lat) * np.pi/360.0)) * k
    return y

#メルカトル座標カラム追加
def node_df_modi(node_df,link_df):
    node_df['lat_world'] = node_df['lat'].apply(wgs84_to_web_mercator_y)
    node_df['lon_world'] = node_df['lon'].apply(wgs84_to_web_mercator_x)
#両端のノードをカラムに追加
def link_df_modi(node_df,link_df):
    lat_s = []
    lon_s = []
    lat_e = []
    lon_e = []
    node_s_list = []
    node_e_list = []
    lon_se = []
    lat_se = []
    for index in range(len(link_df)):
        node_s,node_e = link_node(node_df,link_df,index)
        lat_s.append(node_df['lat'][node_s])
        lon_s.append(node_df['lon'][node_s])
        lat_e.append(node_df['lat'][node_e])
        lon_e.append(node_df['lon'][node_e])
        node_s_list.append(node_s)
        node_e_list.append(node_e)
    link_df['node_s'] = node_s_list
    link_df['node_e'] = node_e_list
    link_df['lat_s'] = lat_s
    link_df['lon_s'] = lon_s
    link_df['lat_e'] = lat_e
    link_df['lon_e'] = lon_e
    link_df['lat_s_world'] = link_df['lat_s'].apply(wgs84_to_web_mercator_y)
    link_df['lon_s_world'] = link_df['lon_s'].apply(wgs84_to_web_mercator_x)
    link_df['lat_e_world'] = link_df['lat_e'].apply(wgs84_to_web_mercator_y)
    link_df['lon_e_world'] = link_df['lon_e'].apply(wgs84_to_web_mercator_x)
    for i in range(len(link_df)):
        lon_se.append([link_df['lon_s_world'][i],link_df['lon_e_world'][i]])
        lat_se.append([link_df['lat_s_world'][i],link_df['lat_e_world'][i]])
    link_df['lon_se_world'] = lon_se
    link_df['lat_se_world'] = lat_se

#リスト、辞書を外部ファイルに保存
#pickle_dump(mydict, './mydict.pickle')
#pickle_load('./mydict.pickle')
def pickle_dump(obj, path):
    with open(path, mode='wb') as f:
        pickle.dump(obj,f)

def pickle_load(path):
    with open(path, mode='rb') as f:
        data = pickle.load(f)
        return data