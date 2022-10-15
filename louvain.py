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
                res += w/2
        return res 

    
    def delta_Q(self, i, c):
        '''
        节点i加入社区c的增益 * 2m (2m 是一个常数)
        '''
        def cal_ki(i):
            ki = 0
            for n, w in self.Graph[i].items():
                ki += w
            return ki + self.C[i].inw

        def cal_kin(i, c):
            kin = 0
            if c in self.Graph[i]:
                kin = self.Graph[i][c]
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
        Res = False
        delta_Qs = [0] * len(self.Graph)
        while Changed:
            Changed = False
            loc = 0
            for i in self.Graph.keys():
                for n in self.Graph[i].keys():
                    c = self.C[n].next_c
                    temp_Q = self.delta_Q(i, c)

                    if temp_Q > delta_Qs[loc]:
                        delta_Qs[loc] = temp_Q
                        Changed = True
                        if c == self.C[i].next_c:
                            continue
                        else:
                            self.C[i].next_c = c
                            # Changed = True 
                            Res = True
                loc += 1  
        return Res
        

                    
    def second_stage(self):
        '''
        重新生成新的网络
        '''
        # 记录网络的节点们
        Record = {}
        for i in self.C.keys():
            c = self.C[i].next_c
            if c not in Record:
                Record[c] = set([i])
            else:
                Record[c].add(i)
        
        # 生成网络
        C = {}
        Graph = {}
        for i in Record.keys():
            # 改变C
            def cal_inw(p):
                inw = 0
                for s in Record[p]: # 遍历子节点
                    for n, w in self.Graph[s].items():
                        if n in Record[p]:
                            inw += w 
                    inw += self.C[s].inw
                return inw 
            

            def cal_subs(p):
                subs = Record[p]
                for n in Record[p]:
                    subs = self.C[n].subs | subs
                return subs
            
            subs = cal_subs(i)
            inw = cal_inw(i)
            C[i] = Nodes(subs, inw, i)

            # 改变graph
            if i not in Graph:
                Graph[i] = {}

            # 仅算子节点
            for n in Record[i]:
                # 防止：当n=i时，把所有子节点又加上了
                # if n == i:
                #     continue
                for s, w in self.Graph[n].items():
                    # 如果是新的网络节点与该子节点之间的连线，则更新至新的节点i
                    # 防止把子节点的连接又加上了
                    if s in Record[i]:
                        continue
                    
                    # 找到子结点的除了父节点以外的连接，对父节点进行更新
                    if s in Record:
                        if s in Graph[i]:
                            Graph[i][s] += w
                        else:
                            Graph[i][s] = w
                        # 从另一边记录边
                        if s not in Graph:
                            Graph[s] = {}
                        if i in Graph[s]:
                            Graph[s][i] += w
                        else:
                            Graph[s][i] = w 
                    else:
                        # 如果不是，则需要先找到s的对应的网络节点，再更新
                        loc = -1
                        for p in Record:
                            if s in Record[p]:
                                loc = p
                                break
                        # 防止：找到的是父节点的其它子节点
                        if loc in Record[i]:
                            continue
                        if loc in Graph[i]:
                            Graph[i][loc] += w
                        else:
                            Graph[i][loc] = w
                        
                        if loc not in Graph:
                            Graph[loc] = {}
                        if i in Graph[loc]:
                            Graph[loc][i] += w
                        else:
                            Graph[loc][i] = w
        
        # # 更新父节点们
        # for i in Record:
        #     for n,w in self.Graph[i].items():
        #         if n in Record:
        #             if n in Graph[i]:
        #                 Graph[i][n] += w
        #             else:
        #                 Graph[i][n] = w

                    # if i in Graph[n]:
                    #     Graph[n][i] += w
                    # else:
                    #     Graph[n][i] = w

        


        self.C = C
        self.Graph = Graph
        
        self.M = self.cal_m()
        print(self.M)
        print(len(self.Graph))


    def excute(self):
        C = True
        while C:
            changed = self.first_stage()
            if changed:
                self.second_stage()
            else:
                C = False

        res = self.get_res()
        self.print_C()
        return res
        
                

    def print_C(self):
        i = 0
        for n in self.C:
            i += 1
            sub = set()
            for s in self.C[n].subs:
                sub.add(s)
            print("节点",i, '--', n, "----", sub)

    
    def get_res(self):
        res = {}
        for n in self.C:
            res[n] = self.C[n].subs
        return res
    



def cal_accuracy(path, dataset) -> float:
    '''
    path: 标签文件的路径。 dataset: 聚类结果{{}, {},...}, 无标签。
    '''
    # 获取原始标签: {label: node}
    Record = {} 
    with open(path, "r") as f:
        for l in f:
            line = l.strip().split()
            n = line[0]
            label = line[1]
            Record[n] = label
    
    # 给数据集dataset加上标签
    labeled = {}
    for n in dataset:
        labels = {}
        for s in dataset[n]:
            l = Record[s]
            if l not in labels:
                labels[l] = 1
            else:
                labels[l] += 1
        res_l = max(labels, key=labels.get)
        labeled[res_l] = dataset[n]
    print(labeled)
    
    # 计算accuracy
    correct, all_nodes = 0, 0
    for i in labeled:
        for j in labeled[i]:
            all_nodes += 1
            if Record[j] == i:
                correct += 1
    
    return correct / all_nodes


def print_origon_dataset(path):
    Record = {} 
    with open(path, "r") as f:
        for l in f:
            line = l.strip().split()
            n = line[0]
            label = line[1]
            if label in Record:
                Record[label].add(n)
            else:
                Record[label] = set([n])
    for n in Record:
        print(n, '--', Record[n])
    return Record




if __name__ == "__main__":
    path = "./dataset/email-Eu-core.txt"
    Graph = gen_graph(path)
    louvain = Louvain(Graph)
    res = louvain.excute()

    path2 = './dataset/email-Eu-core-department-labels.txt'
    ref = print_origon_dataset(path2)

    accuracy = cal_accuracy(path2, res)
    print(accuracy)
