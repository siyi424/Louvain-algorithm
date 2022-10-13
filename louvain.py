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
            kin = 0
            for s in self.C[c].subs:
                if s in self.Graph[i]:
                    kin += self.Graph[i][s]
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
        '''
        确定的是最终的next_c
        '''
        Changed = True
        delta_Qs = [0] * len(self.Graph)
        while Changed:
            Changed = False
            loc = 0
            for i in self.Graph.keys():
                for n in self.Graph[i].keys():
                    c = self.C[n].next_c
                    temp_Q = self.delta_Q(i, c)
                    if temp_Q > delta_Qs[loc]:
                        self.C[i].next_c = c
                        delta_Qs[loc] = temp_Q
                        Changed = True 
                loc += 1  
        res = not Changed
        return res
        

                    
    def second_stage(self):
        Ckeys = set(self.C.keys())
        for i in Ckeys:
            if i == self.C[i].next_c:
                continue
            next_c = self.C[i].next_c

            
            # 改变社区c的信息
            self.C[next_c].subs = self.C[next_c].subs | self.C[i].subs
            for s, w in self.Graph[i].items():
                if self.C[s].next_c == next_c:
                    self.C[next_c].inw += w
            self.C[next_c].inw += self.C[i].inw 

            # 把节点i的links转移到社区next_c
            iTems = list(self.Graph[i].items())
            for s, w in iTems:
                if i == s:
                    continue
                del self.Graph[s][i]
                if s == next_c:    
                    continue
                if s in self.Graph[next_c]:
                    self.Graph[next_c][s] += w
                else:
                    self.Graph[next_c][s] = w
                
                if next_c in self.Graph[s]:
                    self.Graph[s][next_c] += w
                else: 
                    self.Graph[s][next_c] = w
            
            del self.Graph[i]
            del self.C[i]

            
        self.M = self.cal_m()
        print(self.M)


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
