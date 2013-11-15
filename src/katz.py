from igraph import *
import igraph
from itertools import groupby

class Katz:

  visited =set()
  length=[]

  def __init__(self,graph,target):
    self.graph = graph
    self.target = target

  def DFS(self, source, depth):
    #print self.length
    if source.index == self.target.index:
      self.length.append(depth)
      return

    for v in source.neighbors(mode = 'OUT'):
      self.DFS(v,depth+1)

  def get_katz_score(self,source,beta):
    #http://en.wikipedia.org/wiki/Katz_centrality, based on this example

    self.length = []
    self.DFS(source,0)

    counts_dict ={}

    for dist in self.length:
      if dist not in counts_dict:
        counts_dict[dist] = 1
      else:
        counts_dict[dist] += 1

    katz_score=0;

    for k in counts_dict.keys():
      print 'damping',k , pow(beta,k)
      katz_score += pow(beta, k)* counts_dict[k]

    return katz_score

def main():
  graph = igraph.Graph(directed = True)

  graph.add_vertices(7)
  graph.add_edge(0,1)
  graph.add_edge(2,6)
  graph.add_edge(3,1)
  graph.add_edge(2,1)
  graph.add_edge(4,1)
  graph.add_edge(5,1)
  graph.add_edge(6,3)
  graph.add_edge(3,4)
  graph.add_edge(2,3)
  graph.add_edge(4,5)
  graph.add_edge(5,0)

  graph.vs["label"] = ["0", "1", "2","3","4","5","6"]

  target_vertex = graph.vs[1]
  obj = Katz(graph,target_vertex)
  print obj.get_katz_score(graph.vs[6],0.5) 
  print obj.get_katz_score(graph.vs[2],0.5) 
  plot(graph)

if __name__ == '__main__':
  main()