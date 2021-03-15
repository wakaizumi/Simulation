#map描画のメソッド集
#Bokehを利用
import datetime
import bokeh
from bokeh.plotting import figure, output_notebook, show
from bokeh.models import ColumnDataSource
from bokeh.tile_providers import get_provider, Vendors
from bokeh.models import HoverTool
from bokeh.palettes import Pastel1_3    # カラーパレット
from bokeh.transform import factor_cmap # 
from bokeh.io import output_notebook, push_notebook
import ipywidgets as widgets

from def1 import *
from def2_2 import *


"""
mapの描画メソッド
fieldのみの場合、マップを描画
２つの種類の描画対象の指定方法がある　1,agentのリストを渡す　　2,ルートリストを渡す
agent_list = [People,People,,,,]
route_list = [[int,int,,,,],[int,int],,,,,,]
point_nodes [int,int,int,,,]
"""
def draw_map(field,agent_list = None,route_list = None,point_nodes = None,name = 'Map'):

    # Tile Provider Maps の用意
    tile_provider = get_provider(Vendors.CARTODBPOSITRON)

    node = ColumnDataSource(data=field.node_df)
    link = ColumnDataSource(data=field.link_df)

    # 表示範囲を web mercator coordinatesで設定
    # 関東周辺を表示
    x_max = wgs84_to_web_mercator_x(139.78)
    x_min = wgs84_to_web_mercator_x(139.74)
    y_max = wgs84_to_web_mercator_y(35.7)
    y_min = wgs84_to_web_mercator_y(35.665)

    plot = figure(x_range=(x_min, x_max), y_range=(y_min, y_max),
                  plot_width=1000, plot_height=700,
                  x_axis_type="mercator", y_axis_type="mercator",
                  tools='pan, wheel_zoom, reset',
                  title=name)
    plot.add_tile(tile_provider)

    ######################################################################
    # ノードの描画
    cr_node = plot.circle(x='lon_world', y='lat_world', 
                     source=node, 
                     color='blue', alpha=0.5, line_color=None,
                     size=5)

    #強調するノードがある場合
    if point_nodes != None:
        point_node_df = field.node_df.iloc[point_nodes]
        point_node = ColumnDataSource(data=point_node_df)
        plot.circle(x='lon_world', y='lat_world', 
                    source=point_node, 
                    color='green', alpha=0.5, line_color=None,
                    size=10)
    ######################################################################
    #リンクの描画
    link = ColumnDataSource(data = field.link_df)
    cr_link = plot.multi_line(xs="lon_se_world", ys="lat_se_world",
                             source = link, color = 'navy')

    #エージェントの経路描画
    if agent_list != None:
        for i in range(len(agent_list)):
            agent_df = field.link_df.iloc[agent_list[i].log_route]
            agent_link = ColumnDataSource(data = agent_df)
            plot.multi_line(xs="lon_se_world", ys="lat_se_world",
                                source = agent_link, color = 'red')
    
    #ルートの描画
    elif route_list != None:
        for i in range(len(route_list)):
            route_df = link_df.iloc[route_list[i]]
            route_link = ColumnDataSource(data = route_df)
            plot.multi_line(xs="lon_se_world", ys="lat_se_world",
                                source = route_link, color = 'red')

    ############################
    #情報の追加
    hover_node = HoverTool(renderers=[cr_node])
    hover_node.tooltips = [
                      # $ から始めるのは特別なフィールド
                      ('データのindex', '$index'), 
                      # ＠ から始めるのはColumnDataSourceのフィールド
                      ('緯度','@lat'),
                      ('経度','@lon'),
                      ('種類','@name')
                      ]
    plot.add_tools(hover_node)

    hover_link = HoverTool(renderers=[cr_link])
    hover_link.tooltips = [
                      # $ から始めるのは特別なフィールド
                      ('データのindex', '$index'), 
                      # ＠ から始めるのはColumnDataSourceのフィールド
                      ('長さ','@distance')  
                      ]
    plot.add_tools(hover_link)

    ####################
    # 結果表示
    output_notebook()
    show(plot)

"""
プルダウンバーを実装したマップ描画
対象をプルダウンバーによって描画する
"""
def draw_map_pull(field,agent_list = None,route_list = None,point_nodes = None,name = 'Map'):
    
    #ドロップダウンの作成
    active_df_list = {}
    if agent_list != None:
        no_ls = range(len(agent_list))
        d = widgets.Dropdown(options=no_ls, value=0)
        
        for i in range(len(agent_list)):
            active_df_list[i] = field.link_df.iloc[agent_list[i].log_route]
        
    elif route_list != None:
        no_ls = range(len(route_list))
        d = widgets.Dropdown(options=no_ls, value=0)
        
        for i in range(len(route_list)):
            active_df_list[i] = field.link_df.iloc[route_list[i]]
            
            
    ###############################################################
    # Tile Provider Maps の用意
    tile_provider = get_provider(Vendors.CARTODBPOSITRON)

    node = ColumnDataSource(data=field.node_df)
    link = ColumnDataSource(data=field.link_df)

    # 表示範囲を web mercator coordinatesで設定
    # 関東周辺を表示
    x_max = wgs84_to_web_mercator_x(139.78)
    x_min = wgs84_to_web_mercator_x(139.74)
    y_max = wgs84_to_web_mercator_y(35.7)
    y_min = wgs84_to_web_mercator_y(35.665)

    plot = figure(x_range=(x_min, x_max), y_range=(y_min, y_max),
                  plot_width=1000, plot_height=700,
                  x_axis_type="mercator", y_axis_type="mercator",
                  tools='pan, wheel_zoom, reset',
                  title=name)
    plot.add_tile(tile_provider)

    ######################################################################
    # ノードの描画
    cr_node = plot.circle(x='lon_world', y='lat_world', 
                     source=node, 
                     color='blue', alpha=0.5, line_color=None,
                     size=5)

    #強調するノードがある場合
    if point_nodes != None:
        point_node_df = field.node_df.iloc[point_nodes]
        point_node = ColumnDataSource(data=point_node_df)
        plot.circle(x='lon_world', y='lat_world', 
                    source=point_node, 
                    color='green', alpha=0.5, line_color=None,
                    size=10)
    ######################################################################
    #リンクの描画
    link = ColumnDataSource(data = field.link_df)
    cr_link = plot.multi_line(xs="lon_se_world", ys="lat_se_world",
                             source = link, color = 'navy',line_width=2)
    #######################################################################
    #エージェントの経路描画
    def on_value_change(change):
        #すべてのリンクを元に戻す
        plot.multi_line(xs="lon_se_world", ys="lat_se_world",
                                 source = link, color = 'navy')
        agent_index = change['new']
        #描画
        point_link = ColumnDataSource(data = active_df_list[agent_index])
        plot.multi_line(xs="lon_se_world", ys="lat_se_world",
                        source = point_link, color = 'red',line_width=2)
        #現在描画されているagentの番号を標準出力
        print(agent_index)
        push_notebook(handle=t)

    ############################
    #情報の追加
    hover_node = HoverTool(renderers=[cr_node])
    hover_node.tooltips = [
                      # $ から始めるのは特別なフィールド
                      ('データのindex', '$index'), 
                      # ＠ から始めるのはColumnDataSourceのフィールド
                      ('緯度','@lat'),
                      ('経度','@lon'),
                      ('種類','@name')
                      ]
    plot.add_tools(hover_node)

    hover_link = HoverTool(renderers=[cr_link])
    hover_link.tooltips = [
                      # $ から始めるのは特別なフィールド
                      ('データのindex', '$index'), 
                      # ＠ から始めるのはColumnDataSourceのフィールド
                      ('長さ','@distance')  
                      ]
    plot.add_tools(hover_link)

    ####################
    # 結果表示
    d.observe(on_value_change, names='value')
    output_notebook()
    display(d)
    t = show(plot,notebook_handle=True)
#通った道を太く描画するプログラム
def draw_map_traffic(field,agent_list = None,route_list = None,point_nodes = None,name = 'Map'):
    
    #太さを持つdf
    link_df_traffic = field.link_df.copy()
    link_df_traffic['traffic'] = 0
    
    """"
    agent_traffic = {}
    for i in field.G_edges:
        agetn_traffic[i] = 1 #デフォルト値の設定
    """
    agent_traffic_list = [0]*len(link_df_traffic)
    
    if agent_list != None:
        for i in range(len(agent_list)):
            for j in agent_list[i].log_route:
                agent_traffic_list[j] += 1
    
    elif route_list != None:
        for i in range(len(route_list)):
            for j in route_list[i]:
                agent_traffic_list[j] += 1
        
    link_df_traffic.loc[:,'traffic'] = agent_traffic_list
    link_df_traffic_only = link_df_traffic[link_df_traffic['traffic'] != 0]

    ############################################################
    node = ColumnDataSource(data=field.node_df)
    link = ColumnDataSource(data=link_df_traffic)

    # Tile Provider Maps の用意
    tile_provider = get_provider(Vendors.CARTODBPOSITRON)
    
    # 表示範囲を web mercator coordinatesで設定
    # 関東周辺を表示
    x_max = wgs84_to_web_mercator_x(139.78)
    x_min = wgs84_to_web_mercator_x(139.74)
    y_max = wgs84_to_web_mercator_y(35.7)
    y_min = wgs84_to_web_mercator_y(35.665)

    plot = figure(x_range=(x_min, x_max), y_range=(y_min, y_max),
                  plot_width=1000, plot_height=700,
                  x_axis_type="mercator", y_axis_type="mercator",
                  tools='pan, wheel_zoom, reset',
                  title=name)
    plot.add_tile(tile_provider)

    ######################################################################
    # ノードの描画
    cr_node = plot.circle(x='lon_world', y='lat_world', 
                     source=node, 
                     color='blue', alpha=0.5, line_color=None,
                     radius=1)

    #強調するノードがある場合
    if point_nodes != None:
        point_node_df = node_df.iloc[point_nodes]
        point_node = ColumnDataSource(data=point_node_df)
        plot.circle(x='lon_world', y='lat_world', 
                    source=point_node, 
                    color='green', alpha=0.5, line_color=None,
                    size=50)
    ######################################################################
    #リンクの描画
    link = ColumnDataSource(data = link_df_traffic)
    link_traffic = ColumnDataSource(data = link_df_traffic_only)
    cr_link = plot.multi_line(xs="lon_se_world", ys="lat_se_world",
                             source = link, color = 'navy', line_width = 1)
    
    #交通量の描画
    plot.multi_line(xs="lon_se_world", ys="lat_se_world",
                                source = link_traffic, color = 'red', line_width = "traffic")

    ############################
    #情報の追加
    hover_node = HoverTool(renderers=[cr_node])
    hover_node.tooltips = [
                      # $ から始めるのは特別なフィールド
                      ('データのindex', '$index'), 
                      # ＠ から始めるのはColumnDataSourceのフィールド
                      ('緯度','@lat'),
                      ('経度','@lon'),
                      ('種類','@name')
                      ]
    plot.add_tools(hover_node)

    hover_link = HoverTool(renderers=[cr_link])
    hover_link.tooltips = [
                      # $ から始めるのは特別なフィールド
                      ('データのindex', '$index'), 
                      # ＠ から始めるのはColumnDataSourceのフィールド
                      ('長さ','@distance'),
                      ('交通量','@traffic')
                      ]
    plot.add_tools(hover_link)

    ####################
    # 結果表示
    output_notebook()
    show(plot)

#動きをプルダウンバーで表現
def draw_map_dist(field,point_nodes = None,name = 'Map'):
    
    #ドロップダウンの作成
    dist_list = field.dist_log
    no_ls = range(len(dist_list))
    d = widgets.Dropdown(options=no_ls, value=0)

    #描画するデータフレームの作成
    dist_df_list = {} #描画するデータフレームの辞書
    
    for i in range(len(dist_list)):
        link_df_traffic = field.link_df.copy()
        link_df_traffic['traffic'] = 0
        agent_traffic_list = [0]*len(link_df_traffic)
        
        for j in range(len(field.link_df)):
            agent_traffic_list[j] = dist_list[i][j]
        
        link_df_traffic.loc[:,'traffic'] = agent_traffic_list
        link_df_traffic_only = link_df_traffic[link_df_traffic['traffic'] != 0]
        dist_df_list[i] = link_df_traffic_only
            
            
    ###############################################################
    # Tile Provider Maps の用意
    tile_provider = get_provider(Vendors.CARTODBPOSITRON)

    node = ColumnDataSource(data=field.node_df)
    link = ColumnDataSource(data=field.link_df)

    # 表示範囲を web mercator coordinatesで設定
    # 関東周辺を表示
    x_max = wgs84_to_web_mercator_x(139.768)
    x_min = wgs84_to_web_mercator_x(139.762)
    y_max = wgs84_to_web_mercator_y(35.686)
    y_min = wgs84_to_web_mercator_y(35.68)

    plot = figure(x_range=(x_min, x_max), y_range=(y_min, y_max),
                  plot_width=800, plot_height=800,
                  x_axis_type="mercator", y_axis_type="mercator",
                  tools='pan, wheel_zoom, reset, save',
                  title=name)
    plot.add_tile(tile_provider)

    ######################################################################
    # ノードの描画
    cr_node = plot.circle(x='lon_world', y='lat_world', 
                     source=node, 
                     color='blue', alpha=0.5, line_color=None,
                     size=5)

    #強調するノードがある場合
    if point_nodes != None:
        point_node_df = field.node_df.iloc[point_nodes]
        point_node = ColumnDataSource(data=point_node_df)
        plot.circle(x='lon_world', y='lat_world', 
                    source=point_node, 
                    color='green', alpha=0.5, line_color=None,
                    size=10)
    ######################################################################
    #リンクの描画
    link = ColumnDataSource(data = field.link_df)
    cr_link = plot.multi_line(xs="lon_se_world", ys="lat_se_world",
                             source = link, color = 'navy',line_width=2)
    #######################################################################
    #エージェントの経路描画
    def on_value_change(change):
        #すべてのリンクを元に戻す
        plot.multi_line(xs="lon_se_world", ys="lat_se_world",
                                 source = link, color = 'navy',line_width=2)
        field_time = change['new']
        #描画
        point_link = ColumnDataSource(data = dist_df_list[field_time])
        plot.multi_line(xs="lon_se_world", ys="lat_se_world",
                        source = point_link, color = 'red',line_width="traffic")
        #現在描画されているagentの番号を標準出力
        print(field_time)
        push_notebook(handle=t)
        line_df = dist_df_list[field_time].copy()
        line_df['traffic'] = line_df['traffic']+1
        line_link = ColumnDataSource(data = line_df)
        plot.multi_line(xs="lon_se_world", ys="lat_se_world",
                        source = line_link, color = '#f7fbff',line_width="traffic")

    ############################
    #情報の追加
    hover_node = HoverTool(renderers=[cr_node])
    hover_node.tooltips = [
                      # $ から始めるのは特別なフィールド
                      ('データのindex', '$index'), 
                      # ＠ から始めるのはColumnDataSourceのフィールド
                      ('緯度','@lat'),
                      ('経度','@lon'),
                      ('種類','@name')
                      ]
    plot.add_tools(hover_node)

    hover_link = HoverTool(renderers=[cr_link])
    hover_link.tooltips = [
                      # $ から始めるのは特別なフィールド
                      ('データのindex', '$index'), 
                      # ＠ から始めるのはColumnDataSourceのフィールド
                      ('長さ','@distance')  
                      ]
    plot.add_tools(hover_link)

    ####################
    # 結果表示
    d.observe(on_value_change, names='value')
    output_notebook()
    display(d)
    t = show(plot,notebook_handle=True)
    
def draw_map_dens(field,point_nodes = None,name = 'Map'):
    
    #ドロップダウンの作成
    dens_list = field.dens_log
    no_ls = range(len(dens_list))
    d = widgets.Dropdown(options=no_ls, value=0)

    #描画するデータフレームの作成
    dens_df_list = {} #描画するデータフレームの辞書
    
    for i in range(len(dens_list)):
        link_df_traffic = field.link_df.copy()
        link_df_traffic['traffic'] = 0
        agent_traffic_list = [0]*len(link_df_traffic)
        
        for j in range(len(field.link_df)):
            agent_traffic_list[j] = dens_list[i][j] *50
        
        link_df_traffic.loc[:,'traffic'] = agent_traffic_list
        link_df_traffic_only = link_df_traffic[link_df_traffic['traffic'] != 0]
        dens_df_list[i] = link_df_traffic_only
            
            
    ###############################################################
    # Tile Provider Maps の用意
    tile_provider = get_provider(Vendors.CARTODBPOSITRON)

    node = ColumnDataSource(data=field.node_df)
    link = ColumnDataSource(data=field.link_df)

    # 表示範囲を web mercator coordinatesで設定
    # 関東周辺を表示
    x_max = wgs84_to_web_mercator_x(139.768)
    x_min = wgs84_to_web_mercator_x(139.762)
    y_max = wgs84_to_web_mercator_y(35.686)
    y_min = wgs84_to_web_mercator_y(35.68)

    plot = figure(x_range=(x_min, x_max), y_range=(y_min, y_max),
                  plot_width=800, plot_height=800,
                  x_axis_type="mercator", y_axis_type="mercator",
                  tools='pan, wheel_zoom, reset, save',
                  title=name)
    plot.add_tile(tile_provider)

    ######################################################################
    # ノードの描画
    cr_node = plot.circle(x='lon_world', y='lat_world', 
                     source=node, 
                     color='blue', alpha=0.5, line_color=None,
                     size=5)

    #強調するノードがある場合
    if point_nodes != None:
        point_node_df = field.node_df.iloc[point_nodes]
        point_node = ColumnDataSource(data=point_node_df)
        plot.circle(x='lon_world', y='lat_world', 
                    source=point_node, 
                    color='green', alpha=0.5, line_color=None,
                    size=10)
    ######################################################################
    #リンクの描画
    link = ColumnDataSource(data = field.link_df)
    cr_link = plot.multi_line(xs="lon_se_world", ys="lat_se_world",
                             source = link, color = 'navy',line_width=2)
    #######################################################################
    #エージェントの経路描画
    def on_value_change(change):
        #すべてのリンクを元に戻す
        plot.multi_line(xs="lon_se_world", ys="lat_se_world",
                                 source = link, color = 'navy',line_width=2)
        field_time = change['new']
        #描画
        point_link = ColumnDataSource(data = dens_df_list[field_time])
        plot.multi_line(xs="lon_se_world", ys="lat_se_world",
                        source = point_link, color = 'red',line_width="traffic")
        #現在描画されているagentの番号を標準出力
        print(field_time)
        push_notebook(handle=t)
        line_df = dens_df_list[field_time].copy()
        line_df['traffic'] = line_df['traffic']+1
        line_link = ColumnDataSource(data = line_df)
        plot.multi_line(xs="lon_se_world", ys="lat_se_world",
                        source = line_link, color = '#f7fbff',line_width="traffic")

    ############################
    #情報の追加
    hover_node = HoverTool(renderers=[cr_node])
    hover_node.tooltips = [
                      # $ から始めるのは特別なフィールド
                      ('データのindex', '$index'), 
                      # ＠ から始めるのはColumnDataSourceのフィールド
                      ('緯度','@lat'),
                      ('経度','@lon'),
                      ('種類','@name')
                      ]
    plot.add_tools(hover_node)

    hover_link = HoverTool(renderers=[cr_link])
    hover_link.tooltips = [
                      # $ から始めるのは特別なフィールド
                      ('データのindex', '$index'), 
                      # ＠ から始めるのはColumnDataSourceのフィールド
                      ('長さ','@distance')  
                      ]
    plot.add_tools(hover_link)

    ####################
    # 結果表示
    d.observe(on_value_change, names='value')
    output_notebook()
    display(d)
    t = show(plot,notebook_handle=True)