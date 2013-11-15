import os,sys,getopt
import math
import igraph
from igraph import *
import cPickle as pickle


citesMade = 0
citesReceived = 1

backward_graph={}


class Patent_Network:

  def __init__(self):
    self.dg = igraph.Graph(directed = True)
    self.v_indices = {}
    self.vertex_count = 0
    self.dirty = False
    self.topo_order =[]
    self.topo_index ={}

  def build_entire_network(self,filename):
    citeFile = open(filename,'r')
    citeDict ={}
    next(citeFile)

    for line in citeFile:
      line = line.rstrip('\n')
      elems = line.split(',')
      #skip 1st column as the value is irrelevant (line number)
      elems = [int(elems[i]) for i in range(1,len(elems))]
      citingPat,citedPat = elems[0],elems[1]

      (exists_p1,p1_index) = self.add_and_return(citedPat)
      (exists_p2,p2_index) = self.add_and_return(citingPat)

      if(exists_p1 != True):
        self.dg.add_vertex(citedPat)

      if(exists_p2 != True):
        self.dg.add_vertex(citingPat)

      #print line
      self.dg.add_edge(p1_index,p2_index)

    self.dg.simplify()


  def __str__(self):
    return self.dg.summary()


  def add_and_return(self,patent_id):
    if patent_id in self.v_indices:
      return (True,self.v_indices[patent_id])
    else:
      self.v_indices[patent_id] = self.vertex_count
      self.vertex_count = self.vertex_count+1
      return (False,self.v_indices[patent_id])

  def remove_singleton(self):
    for vertex in self.dg.vs:
      if(vertex.indegree() == 0 and vertex.outdegree() == 0):
        self.dirty = True
        self.dg.delete_vertices(vertex.index)

def longest_Path(p,cited, citing):
  cited_index = p.v_indices[cited]

  if(p.topo_order != None):
    p.topo_order = p.dg.topological_sorting()
    p.topo_index = dict([(x[1],x[0]) for x in enumerate(p.topo_order)])

  cited_topo_index = p.topo_index[cited_index]
  long_distance = [-1]*(len(p.topo_order))

  for patent in p.topo_order[cited_topo_index:]:
    #print patent
    for w in p.dg.vs[patent].neighbors():

      long_distance[w.index] = max(long_distance[w.index], long_distance[patent] + 1)


  print long_distance[p.v_indices[citing]]


def build_bc_network(p):
  for patent_vertex in p.dg.vs:
    patent_name = patent_vertex['name']
    g = get_backward_citation(p, patent_name)
    backward_graph[patent_name] = g

def get_backward_citation(p,patent):
  patent_list=[]
  patent_index = p.dg.vs.find(name=patent).index

  patent_list.append(patent_index)

  for v in p.dg.vs[patent_index].neighbors():
    in_neighbours = set([x.index for x in v.neighbors(mode = 'IN')])
    print in_neighbours
    if(patent_index not in in_neighbours):
      patent_list.append(v.index)
    else:
      pass

  return p.dg.induced_subgraph(patent_list,implementation = 'create_from_scratch')

def serialize_object(obj,filename):
    pkl_file = open(filename,'wb')
    pickle.dump(obj, pkl_file)
    pkl_file.close()


def main(argv):
  try:
    opts,args = getopt.getopt(argv,"hd:")
  except getopt.GetoptError:
    print('patent_network.py -d <dict_file>')
    sys.exit(2)

  for opt,arg in opts:
    if opt == '-h':
      print('patent_network.py -d <dict_file> ')
      sys.exit(2)
    elif opt == '-d':
      citationFile = arg

    network_file = 'pickle/network.pkl'
    bc_network_file = 'pickle/bac_network.pkl'
    p = None

    if(os.path.isfile(network_file) == False):
      p = Patent_Network()
      p.build_entire_network(citationFile)
      serialize_object(p,network_file)
      build_bc_network(p)
      serialize_object(backward_graph,bc_network_file)

    elif(os.path.isfile(bc_network_file) == False):
      global backward_graph
      print 'loaded network from pkl'
      print 'building the bc network'
      p = pickle.load(open(network_file,'rb'))
      build_bc_network(p)
      serialize_object(backward_graph,bc_network_file)
    else:
      print 'loaded network from pkl'
      print 'loaded bcnetwork from pkl'
      p = pickle.load(open(network_file,'rb'))
      backward_graph = pickle.load(open(bc_network_file,'rb'))
      print backward_graph[4366336].get_adjacency()

      for vertex in backward_graph[4366336].vs:
        print vertex['name']
      plot(backward_graph[4366336])


if __name__ == '__main__':
  main(sys.argv[1:])
