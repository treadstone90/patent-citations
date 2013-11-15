import pickle
import sys,getopt
import os
import numpy as np
from neg_binomial_regression import *
from networkx import *
import networkx as nx
from numpy import linalg as LA
import katz
from katz import *

bc_network_file = 'pickle/bac_network.pkl'

def average(s): 
  if len(s) == 0:
    return 0
  else:
    return sum(s) * 1.0 / len(s)

#features = [claims, grantYr,citatonLag,corp,gov,fuel,pv,wind,far_external,external,near,other_count]
#Y = [forwardciattions]
# this is part where we do the acutal couting
def getCalculations(patDict,engyCiteDict,classDict,USDict,class_dict,method):
  data_matrix={}
  corp =-1
  gov =-1
  back_network = None

  if(method == 'graph'):
    print 'loading the bc network'
    backward_network = pickle.load(open(bc_network_file,'rb'))

  citeRecList,citeMadeList,citeLagList,claimsList,grantYrList = [],[],[],[],[]
  usCorpList,usGovList,fuelList,PVList,windList = [],[],[],[],[]
  for patent in engyCiteDict:
    features=[]
    # patent is a number
    #features.append(len(engyCiteDict[patent][2]))
    features.append(engyCiteDict[patent][0][1])
    features.append(engyCiteDict[patent][0][2])

    # calculate mean citation lag for each patent
    grantYear = engyCiteDict[patent][0][2]
    lagList = []
    for citedPat in engyCiteDict[patent][2]:
      if citedPat not in patDict:
        continue
      citerGrantYr = patDict[citedPat]
      diff = grantYear - citerGrantYr
      lagList.append(diff)    
    citeLagList.append(average(lagList))

    features.append(average(lagList))

    # calculate number of citations received within 10 year window
    forwardCiteCount = 0
    for citer in engyCiteDict[patent][1]:
      #patent does not have a grant year
      if citer not in patDict:
        continue  
      citerGrantYr = patDict[citer]
      diff = citerGrantYr - grantYear
      # every patent has max of 10 years to receive citations
      if diff <= 10:    
        forwardCiteCount += 1 
    citeRecList.append(forwardCiteCount)
    #features.append(forwardCiteCount)
    y = forwardCiteCount

    # determine if patent was from a US corp., US gov., or neither 
    classSubclass = engyCiteDict[patent][0][4] 
    assignee = engyCiteDict[patent][0][3]

    #some patents don't have an assignee value
    if assignee in USDict:
      if USDict[assignee] == 2:
        corp=1
      if USDict[assignee] == 6:
        gov =1 
    else:
      corp=0
      gov=0

    features.append(corp)
    features.append(gov)

    if classSubclass in classDict:
      if classDict[classSubclass] == 'fuel':
        fuel=1
      else:
        fuel=0
      if classDict[classSubclass] == 'PV':
        pv =1 
      else:
        pv = 0
      if classDict[classSubclass] == 'wind':
        wind =1 
      else:
        wind = 0 
    else:
      fuel=0
      pv=0
      wind=0


    features.append(fuel)
    features.append(pv)
    features.append(wind)
    
    far_ext_count=0
    external_count=0
    near_count = 0
    other_count=0

    super_class_patent = class_dict[patent][0]
    class_patent = class_dict[patent][1]
    sub_class_patent = class_dict[patent][2]
    print patent,super_class_patent
    print "======================="


    # here I need to get call the centrality measure to find the scores
    try:
      if(method == 'graph'):
        graph = backward_network[patent]
        katz_obj = Katz(graph,patent)
    except KeyError, e:
      print ' This node is a singleton node'
      continue


    for backward_citation in engyCiteDict[patent][2]:
      try:
        super_class_back = class_dict[backward_citation][0]
        class_back = class_dict[backward_citation][1]
        sub_class_back = class_dict[backward_citation][2]
      except KeyError, e:
        print 'I got a KeyError - reason "%s"' % str(e)
        continue

      print "FAR EXTERNAL"
      print backward_citation,super_class_back

      print "######################################"
      print "EXTERNAL"
      print backward_citation,class_back

      back_citation_vertex = None

      if(method == 'graph'):
        back_citation_vertex = graph.vs.find(name=back)


      if(super_class_patent != super_class_back):
        if(method == 'nemet'):
          far_ext_count += 1 
        else:
          far_ext_count += obj.get_katz_score(back_citation_vertex)
      elif(class_patent != class_back):
        if(method == 'nemet'):
          external_count += 1
        else:
          external_count += obj.get_katz_score(back_citation_vertex)
      elif(sub_class_patent == sub_class_back):
        if(method == 'nemet'):
          near_count += 1
        else:
          near_count += obj.get_katz_score(back_citation_vertex)
      else:
        if(method == 'nemet'):
          other_count += 1
        else:
          other_count += obj.get_katz_score(back_citation_vertex)

    features.append(far_ext_count)
    features.append(external_count)
    features.append(near_count)
    features.append(other_count)

    print external_count
    print near_count
    print far_ext_count
    print other_count
    print "************************>"

    data_matrix[patent] = (y,features)

  print len(data_matrix)
  print len(engyCiteDict)
  return data_matrix

# this is for the USPTO classification of patents
# this builds the dictionary for every patent, which
# denotes the classes

def build_classes_dict(filename):
  f = open(filename,'r')
  next(f)
  count=0
  class_dict ={}

  for line in f:
    line = line.rstrip('\n')
    elems = line.split('\t')
    patent_id = elems[20].strip()
    super_class = elems[4].strip()
    class_ = elems[24].strip()
    sub_class = elems[18].strip()

    if(patent_id == ''):
      continue
    if(super_class == '' and class_ =='' and sub_class == ''):
      #missed patent count
      print patent_id
      count += 1
      continue;

    patent_id = int(patent_id)
    if patent_id not in class_dict:
      # I can just skip ,cos I checked if a patent can ever have multiple assignments

      # print class_dict[patent_id]
      # value = class_dict[patent_id]
      # value[0] = super_class
      # value[1] = class_
      # value[2] = sub_class
      # if(len(value[0]) > 1):
      #   print value
      #   print "here u are"
      #   sys.exit(2)
      class_dict[patent_id] = [super_class,class_,sub_class]
    else:
      pass

    print class_dict[patent_id]

  return class_dict


def main(argv):
  citationFile = ''
  classSubclassFile = ''
  patentListFile = ''
  completePatDataFile = ''
  assigneeFile = ''
  method_name = 'nemet'
 
  if len(argv) == 0:
    sys.stderr.write('nemet_reproduce.py -p <pickle_file> \n')
    sys.exit(2)
  try:
    opts,args = getopt.getopt(argv,"hp:m:")
  except getopt.GetoptError:
    sys.stderr.write('nemet_reproduce.py -p <pickle_file> \n')
    sys.exit(2)
  for opt,arg in opts:
    if opt == '-h':
      print('nemet_reproduce.py -p <pickle_file> \n')
      sys.exit()
    elif opt == '-p':
      pickle_file = arg
    elif opt == '-m':
      method_name = arg

  data_matrix_file = 'pickle/data_matrix_' + method_name +'.pkl'
  classes_dict_file = 'pickle/classes_dict.pkl'
  # assuming the pickled data are right. Which I hope they are

  if(os.path.isfile(data_matrix_file) == False):
    f = open(pickle_file,"rb")
    completePatDict = pickle.load(f)
    filteredCiteDict = pickle.load(f)
    energyClassDict = pickle.load(f)
    assigneeDict = pickle.load(f)
    f.close()

    if(os.path.isfile(classes_dict_file) == False):
      class_dict = build_classes_dict("ascii_data/pat76_06_assg.asc")
      f = open(classes_dict_file,"wb")
      pickle.dump(class_dict,f)
      f.close()
    else:
      class_dict = pickle.load(open(classes_dict_file,"rb"))

    data_matrix = getCalculations(completePatDict, filteredCiteDict, energyClassDict, assigneeDict, class_dict,method_name)

    f = open(data_matrix_file,"wb")
    pickle.dump(data_matrix, f)
    f.close()

  else:
    data_matrix = pickle.load(open(data_matrix_file,"rb"))
    print data_matrix.keys()
    print data_matrix.values()

    y = []
    x=[]

    for key in data_matrix.keys():
      values = data_matrix[key]
      y.append(values[0])
      x.append(values[1])


    # here we fit a negative binomial regression to the data
    Y = np.array(y)
    X = np.array(x)
    mod = NBin(Y, X)
    res = mod.fit()
    print res.summary()

if __name__ == '__main__':
  main(sys.argv[1:])






  
# to find the Katz index or some other centrality measure
#input is a backward citationnetwork for patent_id
#return a map of centrality scores

# def get_centrality_measure(graph,patent_id):
#   adj_matrix = graph.get_adjacency()
#   vertex_sequence = graph.vs
#   G = nx.DiGraph()

#   for vertex_id in graph.es:
#     print type(vertex_id)
#     print vertex_id
#     source = vertex_id.source
#     target = vertex_id.target
#     patent_1_name = vertex_sequence[source]['name']
#     patent_2_name = vertex_sequence[target]['name']
#     G.add_edge(patent_1_name, patent_2_name)

#   rows=[]
#   for row in adj_matrix:
#     rows.append(row)

#   matrix = np.matrix(rows)
#   eig_val,eig_vec = LA.eig(matrix)
#   phi = max(eig_val)
#   print adj_matrix
#   print adjacency_matrix(G)
#   print matrix

#   print eig_val

#   centrality = nx.katz_centrality_numpy(G,1/(phi*2))
#   print centrality
#   centrality.pop(patent_id)
#   scores = centrality.values();
#   sum_centrality = sum(scores)

#   for patent in centrality.keys():
#     centrality[patent] = (centrality[patent]*1.0)/sum_centrality

#   return centrality

