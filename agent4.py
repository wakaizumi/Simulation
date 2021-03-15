from def1 import *
from def2_2 import *
import copy

#agentの管理、全体の移動
class Field:
    def __init__(self,G,node_df,link_df):
        #マップデータを持つ
        self.node_df = node_df
        self.link_df = link_df
        self.G = G
        self.G_edges = [node_to_link_index(self.node_df,self.link_df,x[0],x[1]) for x in G.edges()] #グラフを構築するリンクindexのリスト
        self.G_nodes = [x for x in self.G.nodes()] #グラフを構築するノードindexのリスト
        self.worldtime = 0
        #マップ内のagentリスト
        self.agent_list = [] #全員
        self.agent_active = [] #ゴールしていない
        self.agent_goal = [] #ゴールした　　active+goal=list
        
        self.dist = {x:0 for x in self.G_edges} #各リンクの人数を持つ辞書
        self.dens = {x:0 for x in self.G_edges} #各リンクの人口密度を持つ辞書
        self.speed = {x:1.2 for x in self.G_edges} #各リンクの速度
        self.dist_log = [] #distを入れる
        self.dens_log = [] #densを入れる
        
    #agentが追加されると呼ばれる
    def agent_add(self,people):
        self.agent_list.append(people)
        self.agent_active.append(people)
    #ゴールすると呼ばれる
    def goal(self,people):
        self.agent_goal.append(people)
        self.agent_active.remove(people)
        
    #呼ばれた時点での分布を計算 {リンク番号:人数}
    def __distribution(self):
        self.dist = {x:0 for x in self.G_edges}
        #self.dist[None] = 0
        for i,v in enumerate(self.agent_active):
            pos = v.position_link
            self.dist[pos] += 1
        self.dist_log.append(self.dist)
        
        self.__density()
    
    #その瞬間の人口密度，速度の計算　人口密度ログを取る
    def __density(self):
        def f_speed(x):return max(1.356-0.341 * x,0.1) #フルーインの式
        #リセット
        self.dens = {x:0 for x in self.G_edges}
        self.speed = {x:1.2 for x in self.G_edges}
        
        #すべての辺に対して人口密度，速度を計算
        for i in self.G_edges:
            people_num = self.dist[i]
            if people_num == 0: continue
            
            x = self.link_df.width[i]
            w = 0
            if x == 1 :w = 0.5
            elif x == 2:w = 1.5
            elif x == 3:w = 2.5
            elif x == 4:w = 3.5
            elif x == 99:w = 0.1
            area = self.link_df.distance[i] * w
            self.dens[i] = people_num / area
            self.speed[i] = round(f_speed(people_num / area),1)
        self.dens_log.append(self.dens)
    
    def simulation(self,time_limit=float('inf')):
        #activeなエージェントがいる間
        while (self.agent_active):
            self.worldtime+=1
            if(self.worldtime>=time_limit):return
            
            self.set_speed()
            self.move_agent()
            print(self.worldtime)
            
    #全員の速度を決定
    def set_speed(self):
        self.__distribution()
        for agent in self.agent_active:
            agent.v = self.speed[agent.position_link]
    def move_agent(self):
        for agent in self.agent_active:
            agent.move()
    
    #エージェントの追加
    def people_appearance(self,start,end,num,people_type):
        for i in range(num):
            p = type(people_type)(self,start,end)
            self.agent_add(p)

class People:
    def __init__(self,field,pos_node,end):
        #デフォルトでは行動指針に最短経路を設定する
        #next_node,next_link,start_link,use_link_index = a_star(field,pos_node,end,a_star_type=0)
        next_node,next_link,start_link,use_link_index = shortest_path(field,pos_node,end)
        self.field = field
        #位置情報
        self.start = pos_node
        self.position_node = pos_node #ノードindex
        self.position_link = start_link #リンクindex
        self.advanced  = 0
        #状態
        self.next_node = next_node #辞書型
        self.next_link = next_link #辞書型
        self.before_node = None
        self.destination = end #ノードindex
        self.survival_time = 0
        self.birth_time = self.field.worldtime #生成された時間
        self.v = 0
        #ログ
        self.log_route = [] #通ったルートのリンク番号
        self.log_dens = [] #人口密度のログ
        self.log_neig = [] #人数
    
    #移動メソッド
    def move(self):
        self.log_dens.append(self.field.dens[self.position_link])
        self.log_neig.append(self.field.dist[self.position_link])
        self.survival_time += 1
        self.advanced += self.v #スピード分進める
        #次のノードについた時
        if self.advanced >= weight_get(self.field.node_df,self.field.link_df,self.position_node,self.next_node[self.position_node]):
            #次のノードがゴールの場合
            if self.next_node[self.position_node] == self.destination:
                self.__proceed()
                return
            if self.next_link[self.position_link] == None:
                self.__proceed()
            elif self.field.speed[self.next_link[self.position_link]] > 0.1:
                self.__proceed()

    #次のノードに進めるメソッド
    def __proceed(self):
        #ルートログを記録
        self.log_route.append(self.position_link)
        self.before_node = self.position_node
        self.position_node = self.next_node[self.position_node]
        #ゴールした時
        if self.position_node == self.destination or self.next_link[self.position_link] == None:
            self.position_link = None
            self.field.goal(self)
            return
        self.position_link = self.next_link[self.position_link]
        self.advanced = 0

#古い混雑考慮アルゴリズム
class People1(People):
    
    def __init__(self,field,pos_node,end,threshold = 0.6):
        super().__init__(field,pos_node,end)
        self.speed_threshold = threshold #この数値以下の速度になったら再検索
        self.change_count = 0 #経路を再検索した回数

    def move(self):
        #ノードにいてスピードが落ちたとき、経路を再検索
        if self.next_link[self.position_link] != None:
            if self.advanced == 0 and self.field.speed[self.next_link[self.position_link]] <= self.speed_threshold:
                self.__research()
                self.change_count += 1
        super().move()
    
    def __research(self):
        next_node,next_link,start_link,use_link_index = a_star(self.field,self.position_node,self.destination,a_star_type=1)
        self.position_link = start_link
        self.next_node = next_node 
        self.next_link = next_link
        
class People3(People):
    
    def __init__(self,field,pos_node,end,threshold = 0.25):
        super().__init__(field,pos_node,end)
        self.dens_threshold = threshold #この数値以下の速度になったら再検索
        self.change_count = 0 #経路を再検索した回数
    
    #ルートが無いとき待つ
    """
    def move(self):
        #ノードにいてスピードが落ちたとき、経路を再検索
        if self.next_link[self.position_link] != None:
            if self.advanced == 0 and self.field.dens[self.next_link[self.position_link]] <= self.dens_threshold:
                if(self.__research()== False): return
                self.change_count += 1
        super().move()
    """
    def move(self):
        #ノードにいてスピードが落ちたとき、経路を再検索
        if self.next_link[self.position_link] != None:
            if self.advanced == 0 and self.field.dens[self.next_link[self.position_link]] <= self.dens_threshold:
                #if(self.__research()== False): return
                self.change_count += 1
        super().move()
        
    def __research(self):
        next_node,next_link,start_link,use_link_index = a_star_dens(self.field,self.position_node,self.destination)
        if next_link != None:
            self.position_link = start_link
            self.next_node = next_node 
            self.next_link = next_link
            return True
        else: return False
        
#確率で選択する。
class People2(People):
    def __init__(self,field,pos_node,end):
        super().__init__(field,pos_node,end)
        self.pro_list = [] #どんな確率を取ってきたのかのログ
        self.time_list = [] #候補ルートの時間のログ
        self.interval = 0
        self.astar_type = 0
        
    def move(self):
        if self.interval > 0: self.interval -= 1 #カウントを減らす
        #分岐点に来たときに
        if self.advanced == 0 and len(self.field.G.edges(self.position_node)) >= 3:
            self.branch()
        super().move()
        
    def branch(self):
        #intervalが0以下でないと経路の再選択はしない
        if self.interval <= 0:
            t_list,cand_node_list,next_node_list,next_link_list = self.time_prediction()
            
        #確率を計算する
            next_index = self.probability_selection(t_list)
            #self.position_link = node_to_link_index(self.field.node_df,self.field.link_df,self.position_node,cand_node_list[next_index])
            self.next_node = next_node_list[next_index]
            self.next_link = next_link_list[next_index]
            self.position_link = node_to_link_index(self.field.node_df,self.field.link_df,self.position_node,self.next_node[self.position_node])
            #intervalを再設定
            self.interval = random.randint(60,300) #1分から5分
        
     #候補となるルートとかかる時間を求める(分岐点にいる前提)
    def time_prediction(self):
        t_list = [] #候補ノードからゴールまでの最短時間
        cand_node_list = [] #候補ノードのリスト

        cand_next_node_list = []
        cand_next_link_list = []
        cand_start_link_list = []

        #周りのリンクに対して(現在ノード,その先のノード)
        for (x,nc) in self.field.G.edges(self.position_node):
            #ゴールの候補ノードがあった場合
            if nc == self.destination:
                t_list = [1]
                cand_node_list = [nc]
                cand_next_node_list = [{self.position_node:nc}]
                cand_next_link_list = [{self.position_link:None}]
                break
            #戻らないノードにおいて-------------------------------------------------------------
            elif nc != self.before_node:
                #混雑は考慮しない最短経路　戻らないように現在位置を削除した探索
                #next_node,next_link,start_link,use_link_index = a_star(self.field, nc, self.destination, a_star_type = self.astar_type, remove_node_list=[self.position_node])
                #それぞれのルートを算出する
                next_node,next_link,start_link,use_link_index = random_route(self.field,nc,self.destination,remove_node_list=[self.position_node])
                
                #ルートがない場合
                if use_link_index == None:
                    continue
                t = 0
                #混雑が考慮されない場合
                if self.astar_type == 0:
                    for link in use_link_index: 
                        t += self.field.link_df.distance[link] / 1.2 #ルートを進むのにかかる時間を追加
                    t += weight_get(self.field.node_df,self.field.link_df,self.position_node,nc)/ 1.2 #現在地から見ているノードまでの時間を追加
                #混雑が考慮される場合
                else:
                    for link in use_link_index: 
                        t += self.field.link_df.distance[link] / self.field.speed[link]#ルートを進むのにかかる時間を追加
                    t += weight_get(self.field.node_df,self.field.link_df,self.position_node,nc)/ self.field.speed[start_link]
                t_list.append(t)
                cand_node_list.append(nc)

                next_node.setdefault(self.position_node,nc)#現在地から次のノードまでのルートが入っていないため
                next_link.setdefault(node_to_link_index(self.field.node_df,self.field.link_df,self.position_node,nc),start_link)#同様
                #next_node[self.position_node] = nc
                #next_link[node_to_link_index(self.field.node_df,self.field.link_df,self.position_node,nc)] = start_link
                cand_next_node_list.append(next_node)
                cand_next_link_list.append(next_link)
                cand_start_link_list.append(start_link)
                
        return t_list,cand_node_list,cand_next_node_list,cand_next_link_list


    #時間のリストから確率でどれかを選ぶ
    def probability_selection(self,t_list):
        def f1(x):return max(-x+2,0)
        rati = [] #計算した確率を入れるリスト
        min_t = min(t_list) #リスト内の時間最小値を入れる
        for i,v in enumerate(t_list) :
            x = v / min_t #最小との比率を計算
            rati.append(f1(x))
            
        #確率の算出
        probability = [] #合計1になるように
        for i,v in enumerate(rati):
            pro = rati[i] / sum(rati)
            probability.append(pro)
        self.pro_list.append(probability)
        self.time_list.append((t_list,self.position_node))

        #確率的に次のノードを選択
        next_index = np.random.choice(range(len(probability)),p = probability)
        return next_index
    
#確率的要素にスピードの混雑考慮を加える
class People2_1(People2):
    def __init__(self,field,pos_node,end):
        super().__init__(field,pos_node,end)
        self.astar_type = 1
        
#一つ前のリンクの人口密度が高いときその場に止まる
class People2_2(People2):
    
    def __init__(self,field,pos_node,end):
        super().__init__(field,pos_node,end)
    
    def move(self):
        #進む先のリンクが混んでいるとき→止まる
        if self.next_link[self.position_link] != None:
            if self.field.dens[self.next_link[self.position_link]] >= 0.3: #この閾値は適当
                return
        super().move()