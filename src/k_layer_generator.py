#!/usr/bin/env python3
import sys,getopt
import math
from collections import defaultdict
import cPickle as pickle


citeInfo = []
numPatentsInKLayer = {}
citesMade = 0
citesReceived = 1

sys.setrecursionlimit(2000)

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


def genKLayers(patentNum,citeDict,filename):
  KLayers = [set([])]
  if patentNum not in citeDict:
    return 

  citations = set(citeDict[patentNum][citesMade])
  klayerFilename = str(filename) + '_KLayers.csv'
  outfile = open(klayerFilename,'w')

  #generate KL1
  for patent in citations:
    singleton = set([patent])
    otherCites = list(citations - singleton)
    cited = False

    for c2 in otherCites:
      if c2 in citeDict[patent][citesReceived]:
        cited = True
    #if patent doesn't received any cites, then it belongs in KL1 
    if not cited:
        KLayers[0].add(patent) 

  for sourcePat in KLayers[0]:
    output = str(sourcePat) + ',' + 'KL1' + '\n' 
    outfile.write(output) 
  #print('remaining IDs to be placed in KL or not', citations - KLayers[0])
  remainingCites = citations - KLayers[0]
  numRemainingCites = len(remainingCites)
  index = 0

  #generate remaining KLayers
  while numRemainingCites > 0:
    KLayers.append(set([]))
    unconnected = set([])
    for cite in remainingCites:
      LayerCheck = False
      singleton = set([cite])
      # otherCites should be IDs outside 
      outerKLIDs = list(citations - KLayers[index] - singleton)
      for elem in KLayers[index]:
        #citation from previous layer citing possible element in current knowledge layer
        if elem in citeDict[cite][1]:
          LayerCheck = True
      for elem in outerKLIDs:
        #citation being check that it has been cited by others outside previous knowledge layer 
        if elem in citeDict[cite][1]:
          LayerCheck = False
      if LayerCheck is True:
        KLayers[index+1].add(cite) 
        output = str(cite) + ',' + 'KL' + str(index+2) + '\n' 
        outfile.write(output) 
    #remove elements that do not satesify knowledge layer requirements

    for cite in remainingCites:
      if len(KLayers[index + 1]) == 0:
        unconnected.add(cite)
    remainingCites -= (KLayers[index + 1] | unconnected)
    numRemainingCites = len(remainingCites)
    index += 1

  sumKLayers = 0 
  for layer in KLayers:
    sumKLayers += len(layer)
  #first param is KL1 index, second param is forward citations
  if sumKLayers != 0:
    citeInfo.append((float(len(KLayers[0]))/sumKLayers,len(citeDict[patentNum][1])))
  else:
    citeInfo.append((0,len(citeDict[patentNum][1])))
  
  numLayers = len(KLayers)
  numElemsKL1 = len(KLayers[numLayers - 1])
  if numElemsKL1 == 0:
    numLayers -= 1
  if numLayers in numPatentsInKLayer:
    numPatentsInKLayer[numLayers] += 1
  else:
    numPatentsInKLayer[numLayers] = 1
 
  outfile.close()


def runIDs(filename,citeDict,path):
  inputFile = open(filename, 'r')
  outFile = open('KL1_forward_cite_graph_data.csv','w')
  outFile2 = open('max_total_klayers.csv','w')
  for patent in inputFile:
    patent = patent.rstrip('\n') 
    filename = path + str(patent)
    genKLayers(int(patent),citeDict,filename)
  for elem in citeInfo:
    xValue,yValue = elem[0],elem[1]
    output = str(xValue) + ',' + str(yValue) + '\n'
    outFile.write(output)
  for elem in numPatentsInKLayer:
    xValue,yValue = elem,numPatentsInKLayer[elem]
    output = str(xValue) + ',' + str(yValue) + '\n'
    outFile2.write(output)
  
  inputFile.close
  outFile.close
  outFile2.close

def main(argv):
  patentList = '' 
  citationFile = ''   
  path = '' 
  if len(argv) == 0:
    print('getAnalytics.py -i <input patentIDs> -c <citation file> -p <output directory>')
    sys.exit(2)
  try:
    opts,args = getopt.getopt(argv,"hc:i:p:")
  except getopt.GetoptError:
    print('getAnalytics.py -i <input patentIDs> -c <citation file> -p <output directory>')
    sys.exit(2)
  for opt,arg in opts:
    if opt == '-h':
      print('getAnalytics.py -i <input patentIDs> -c <citation file> -p <output directory>')
      sys.exit()
    elif opt == '-c':
      citationFile = arg
    elif opt == '-i':
      patentList = arg      
    elif opt == '-p':
      path = arg    
 
  citationDict = getCitations(citationFile)
  runIDs(patentList,citationDict,path)
  
  print 'starting to pickle'
  output = open('dict.pkl','wb')
  print 'starting to pickle'
  pickle.dump(citationDict,output)
  print 'cosng strem'
  output.close()



if __name__ == '__main__':
  main(sys.argv[1:])
