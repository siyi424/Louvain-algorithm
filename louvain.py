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
    def __init__(self, subs):
        self.subs = subs


class Louvain():
    def __init__(self, Graph):
        self.Graph = Graph
        self.C = {}
        for n in self.Graph.keys():
            subs = set([n]) # 社区的代表是n，所以社区需要包含n本身
            nodes = Nodes(subs)
            self.C[n] = nodes

        self.M = self.cal_m() 
    
    
    def cal_m(self):
        res = 0
        for n in self.Graph.keys():
            for s, w in self.Graph[n].items():
                res += w
        return res / 2
    
    
    def delta_Q(self, i, c):
        '''
        节点i加入社区c的增益Q * 2m (2m 是一个常数)
        '''
        def cal_ki(i):
            ki = 0
            for n, w in self.Graph[i].items():
                ki += w
            return ki * 2

        def cal_kin(i, c):
            kin = 0
            if c in self.C.keys():
                for n in self.C[c].subs:
                    if n in self.Graph[i]:
                        kin += self.Graph[i][n]
            return kin 
        
        def cal_tot(c):
            tot = 0
            for s, w in self.Graph[c].items():
                tot += w
            return tot


        ki = cal_ki(i)
        kin = cal_kin(i, c)
        tot = cal_tot(c)

        delta_Q = kin  - tot * ki / self.M
        return delta_Q
    

    def first_stage(self):
        '''
        return [i, c] or False
        考虑节点与节点、节点与社区、社区与社区之间的关系
        '''
        for i in self.C.keys():
            delta_Q = 0
            next_c = i
            for n in self.Graph[i].keys():
                temp_Q = self.delta_Q(i, n)
                if temp_Q > delta_Q:
                    next_c = n
                    delta_Q = temp_Q
            if next_c != i:
                return [i, next_c]
        return False

                    
    def second_stage(self, i, next_c):
        self.C[next_c].subs = self.C[next_c].subs | self.C[i].subs  # 社区与社区的合并
        del self.C[i]

        # 图压缩
        # 节点i的和社区以外的节点的连线，需要都转移到节点next_c上。如果一个节点两个都连了，则权值相加。
        # 节点i仍保留和社区内部的连线
        # 社区与社区子节点们的转移
        
        record = {}
        for s, w in self.Graph[i].items():
            record[s] = w
    
        for s, w in record.items():
            if s in self.C[next_c].subs:
                continue
            if s in self.Graph[next_c]:
                self.Graph[next_c][s] += w
            else:
                self.Graph[next_c][s] = w

            del self.Graph[i][s]


    def excute(self):
        Changed = True
        while Changed:
            res = self.first_stage()
            print(res)
            if res:
                i, next_c = res
                self.second_stage(i, next_c)
                Changed = True
            else:
                Changed = False
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
