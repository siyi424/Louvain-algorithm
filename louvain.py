# 生成网络
def gen_graph(path):
    '''
    Graph 的结构为： {node1: {neighbor1: weight, neighbor2: weight,...},...}
    对于email-Eu-core数据集,weight=1
    '''
    Graph = {}
    with open(path, "r") as f:
        for l in f:
            line = l.strip().split()
            n1 = line[0]
            n2 = line[1]
            w = 1
            if n1 not in Graph:
                Graph[n1] = {}
            if n2 not in Graph:
                Graph[n2] = {}
            Graph[n1][n2] = w
            Graph[n2][n1] = w
    return Graph



# 每个社区的信息
class Nodes():
    def __init__(self, subs, inw, next_c):
        self.subs = subs
        self.inw = inw # 环的权重
        self.next_c = next_c # 在firststage中记录最近的neighbor


class Louvain():
    def __init__(self, Graph):
        self.Graph = Graph
        self.C = {}
        for n in self.Graph.keys():
            subs = set([n]) # 社区的代表是n，所以社区需要包含n本身
            nodes = Nodes(subs, 0, n)
            self.C[n] = nodes

        self.M = self.cal_m() 
    
    
    def cal_m(self):
        '''
        = 图内的边 / 2 + 每个社区的inw
        '''
        res = 0
        for n in self.Graph.keys():
            for s, w in self.Graph[n].items():
                res += w / 2
            res += self.C[n].inw
        return res
    
    
    def delta_Q(self, i, c):
        '''
        节点i加入社区c的增益 * 2m (2m 是一个常数)
        '''
        def cal_ki(i):
            ki = 0
            for n, w in self.Graph[i].items():
                ki += w
            return ki

        def cal_kin(i, c):
            kin = self.Graph[c][i]
            return kin 
        
        def cal_tot(c):
            tot = 0
            for s, w in self.Graph[c].items():
                tot += w
            return tot + self.C[c].inw


        ki = cal_ki(i)
        kin = cal_kin(i, c)
        tot = cal_tot(c)

        delta_Q = kin  - tot * ki / self.M
        return delta_Q
    

    def first_stage(self) -> bool:
        Changed = False
        for i in self.C.keys():
            delta_Q = 0
            for n in self.Graph[i].keys():
                temp_Q = self.delta_Q(i, n)
                if temp_Q > delta_Q:
                    self.C[i].next_c = n
                    Changed = True
        return Changed
        

                    
    def second_stage(self):
        # 记录改变的位置，方便graph压缩查询
        record = {}
        
        def search(next_c) -> int:
            fc = next_c
            if next_c not in record:
                return fc
            while True:
                fc = record[fc]
                if fc not in record:
                    break
            return fc
                    

        for i in self.C.keys():
            next_c  =self.C[i].next_c
            # 节点i没有更新社区时
            if next_c == i:
                continue
            
            # 节点i需要更新社区时，找到最终的社区fc
            fc = search(next_c)
            record[i] = fc
            print(record[i])

            self.C[fc].subs = self.C[fc].subs | self.C[i].subs
            self.C[fc].inw = self.C[i].inw + self.Graph[i][fc] * 2 + self.C[fc].inw
            

            temp = {}
            for s, w in self.Graph[i].items():
                temp[s] = w

            # 把节点i的links转移到社区fc
            for s, w in temp.items():
                if s in self.Graph[fc]:
                    self.Graph[fc][s] += w
                else:
                    self.Graph[fc][s] = w
                
                if fc in self.Graph[s]:
                    self.Graph[s][fc] += w
                else: 
                    self.Graph[s][fc] = w
                del self.Graph[s][i]
        
        # 删除
        for d in record.keys():
            del self.C[d]
            del self.Graph[d]


        self.M = self.cal_m()


    def excute(self):
        C = True
        while C:
            changed = self.first_stage()
            if changed:
                self.second_stage()
            else:
                C = False
        self.print_C()
                

    def print_C(self):
        i = 0
        for n in self.C:
            i += 1
            sub = set()
            for s in self.C[n].subs:
                sub.add(s)
            print("节点",i, '--', n, "----", sub)
            



if __name__ == "__main__":
    path = "./dataset/email-Eu-core.txt"
    Graph = gen_graph(path)
    louvain = Louvain(Graph)
    louvain.excute()
