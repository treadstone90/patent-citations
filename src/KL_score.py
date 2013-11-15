import os,sys,getopt
import math
from collections import defaultdict
import cPickle as pickle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab



# the program will read every file in that directory and then calculate the KL score for every patent 
#in that diretory
# So for every file I will have a dictionary as the outpu which gives patent Number and score

# Visulziatonas
#1. Patets that arr globally important by just summing up the scores

#2. Then for histogram of highest and lowest scores usng this metric

#3. Histogram maximum KL-depth

#4. The Correlation between the KL score and the number of frorward citations.

#usage - python KL_score.py -c cite76_06.csv,\test2
# output - one dict with id : {list(tuple)}

citesMade = 0
citesReceived = 1
kl_score ={}

patent_global_score={} # then we need to find the rank

kl_score_max_min={} # score the maximum 

patent_global_forward={} # then we need to get the rank



delta=0.5

def getCitations(filename):
  citeFile = open(filename,'r')
  citeDict = {} 
  
  #skip header info
  next(citeFile)
  for line in citeFile:
    line = line.rstrip('\n')
    elems = line.split(',')
    #skip 1st column as the value is irrelevant (line number)
    elems = [int(elems[i]) for i in range(1,len(elems))]
    citingPat,citedPat = elems[0],elems[1]

    if citingPat in citeDict:
      citeDict[citingPat][citesMade].append(citedPat)
    else:
      citeDict[citingPat] = ([citedPat],[])
    if citedPat in citeDict:
      citeDict[citedPat][citesReceived].append(citingPat)
    else:
      citeDict[citedPat] = ([],[citingPat])

  citeFile.close()
  return citeDict

def gen_statistics():
  kl_max=[]
  kl_min=[]
  score_max=[]
  score_min=[]

  for key,ranked_citations in kl_score.iteritems():

    for entry,score in ranked_citations:

      if entry[0] in patent_global_score:
        patent_global_score[entry[0]] = patent_global_score.get(entry[0]) + score
      else:
        patent_global_score[entry[0]] = score

    # kl_score_max_min[key] = (ranked_citations[0][0][1],ranked_citations[0][1],
    #   ranked_citations[-1][0][1],ranked_citations[-1][1]) # (kl_max,max_score,kl_min,min_score)

    kl_max.append(ranked_citations[0][0][1])
    kl_min.append(ranked_citations[-1][0][1])

    score_max.append(ranked_citations[0][1])
    score_min.append(ranked_citations[-1][1])

  # first for max_KL
  plot_histogram(kl_max,'histogram of maximum kl_index');
  plot_histogram(kl_min,'histogram of mnimum kl_index');



def plot_histogram(x,plot_label):
  
  fig = plt.figure()
  ax = fig.add_subplot(111)

  # the histogram of the data
  n, bins, patches = ax.hist(x, 10, normed=0, facecolor='green', alpha=0.75)

  bincenters = 0.5*(bins[1:]+bins[:-1])
  ax.set_xlabel('KL-Index')
  ax.set_ylabel(plot_label)
  ax.set_xlim(0, 5)
  ax.set_ylim(0, 500)
  ax.grid(True)

  plt.show()

def write_results():
  out_file = open('kl_score.txt','w')

  for key,ranked_citations in kl_score.iteritems():
    out_file.write(key+':-----'+str((ranked_citations)))
    out_file.write('\n')


def generatekl_score(directory,citationDict):
  for file_name in os.listdir(directory):
    file_path = os.path.join(directory,file_name)

    if os.path.isfile(file_path):
      print file_path
      find_score(file_path, citationDict)



def find_score(file_path,citationDict):
  f = open(file_path)
  entries=[]
  height=0;
  patent_set = set()
  ranked_citations = []

  for line in f.readlines():
    elems = line.split(',')
    kl_index = elems[1].strip()
    patent_id = elems[0].strip()

    entries.append( (int(patent_id), int(kl_index[-1])))
    height = max(height,int(kl_index[-1]))
    patent_set.add(int(elems[0]))

  for entry in entries:
    backward_citations = set(citationDict[entry[0]][0])
    inDegree = len(backward_citations.intersection(patent_set))
    patent_depth = entry[1]
    score = 1 + height - patent_depth - delta*inDegree
    ranked_citations.append((entry,score))

  ranked_citations.sort(key=lambda x: x[1],reverse=True)
  file_name = os.path.split(file_path)[1]

  if len(ranked_citations) > 0:
    kl_score[file_name.split('_')[0]] = ranked_citations


def plot_kl_index_histgram(citationDict):


  results_dict={}
  kl_index_list=[]
  fwd_citations =[]
  empty_count=0

  for patent in citationDict.keys():
    forward_citations = len(citationDict[patent][citesReceived])

    # now to find the KL-i indexci

    file_name = "test2/"+str(patent) + "_KLayers.csv"
    count =0
    backward_count=0

    if(os.path.isfile(file_name) == False):
      continue

    f = open(file_name,'r')

    for line in f.readlines():
      kl = int((line.strip().split(',')[1].strip())[-1])
      if(kl == 1):
        count += 1

      backward_count += 1

    if(count > 0):
      kl_one_index = 1.0*count/backward_count
    else:
      kl_one_index = 0
      print 'pass.....'
      empty_count += 1
      continue

    #print count , ":",backward_count,":",kl_one_index
    
    key = int(kl_one_index*10)

    if key not in results_dict:
      results_dict[key] = [forward_citations]
    else:
      results_dict[key].append(forward_citations)

    kl_index_list.append(kl_one_index)
    fwd_citations.append(forward_citations)

  print empty_count
  return results_dict, kl_index_list, fwd_citations

def main(argv):
  pass
  patentList = '' 
  citationFile = ''
  pkl= None
  graph_pkl =None
  
  if len(argv) == 0:
    print('KL_Score.py -c <cite file> -d <KL directory>')
    sys.exit(2)

  try:
    opts,args = getopt.getopt(argv,"hc:d:p:")
  except getopt.GetoptError:
    print('KL_Score.py -c <cite file> -d <KL directory>')
    sys.exit(2)

  for opt,arg in opts:
    if opt == '-h':
      print('KL_Score.py -c <cite file> -d <KL directory>')
      sys.exit(2)
    elif opt == '-c':
      citationFile = arg
    elif opt == '-d':
      directory = arg
    elif opt == '-p':
      pkl = arg

  if pkl == None:
    citationDict = getCitations(citationFile)
    graph_dict,kl_index_list,fwd_citations = plot_kl_index_histgram(citationDict)
    generatekl_score(directory,citationDict)
    out_file = open('kl_score.pkl','wb')

    graph_file = open('kl_index_list.pkl','wb')
    pickle.dump(kl_index_list,graph_file)
    graph_file.close()

    graph_file = open('fwd_citations_list.pkl','wb')
    pickle.dump(fwd_citations,graph_file)
    graph_file.close()

    graph_file = open('graph_dict.pkl','wb')
    pickle.dump(graph_dict,graph_file)
    graph_file.close()

    global kl_score
    pickle.dump(kl_score, out_file)
    out_file.close()

  else:
    global kl_score
    print 'gotcha'
    print pkl
    pickled_data = pickle.load(open(pkl,'rb'))
    print pickled_data[8]


if __name__ == '__main__':
  main(sys.argv[1:])