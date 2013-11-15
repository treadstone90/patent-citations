#!/usr/bin/env python
import sys,getopt
import math
from collections import defaultdict
import pickle
import csv

def average(s): 
  if len(s) == 0:
    return 0
  else:
    return sum(s) * 1.0 / len(s)

def median(mylist):
  if len(mylist) == 0:
    return 0
  else:
    sorts = sorted(mylist)
    length = len(sorts)
    if not length % 2:
      return (sorts[length // 2] + sorts[length // 2 - 1]) / 2.0
    return sorts[length // 2]

def stdDev(inputList,mean):
  if len(inputList) == 0:
    return 0
  else:
    variance = list(map(lambda x: (x - mean)**2, inputList))
    return math.sqrt(average(variance))

def printVariableData(variableName, variableList):
  print(variableName,'\t')
  for i in range(len(variableList)):
    print (variableList[i],'\t')
  print('')

def outputAnalytics(variableList):
  for varName,varList in variableList:
    printVariableData(varName,varList)

#generates data for Figure 3 from Nemet's 2012 paper
def getCitationsWithin10Yrs(patDict, citationDict):
  totalCitations = []
  for patent in citationDict:
    grantYr = citationDict[patent][0][2]
    count = 0
    for elem in citationDict[patent][1]:
      if elem not in patDict:
        continue
      citeYr = patDict[elem]
      diff = citeYr - grantYr
      if diff <= 10:
        count += 1
    totalCitations.append(count)
  
  totalCiteDict = defaultdict(int) 
  for elem in totalCitations:
    totalCiteDict[elem] += 1
  
  outfile = open('citations_10_years.csv','w')
  for key in totalCiteDict:
    output = str(key) + ',' + str(totalCiteDict[key])+'\n'
    outfile.write(output)
  outfile.close() 

def getCalculations(patDict,engyCiteDict,classDict,USDict):
  citeRecValues = [0.0]*5 
  citeMadeValues = [0.0]*5
  citeLagValues = [0.0]*5
  claimsValues = [0.0]*5
  grantYrValues = [0.0]*5
  usCorp = [0.0]*3
  usGov = [0.0]*3
  fuel = [0.0]*3
  PV = [0.0]*3
  wind = [0.0]*3
  citeRecList,citeMadeList,citeLagList,claimsList,grantYrList = [],[],[],[],[]
  usCorpList,usGovList,fuelList,PVList,windList = [],[],[],[],[]
  for patent in engyCiteDict:
    citeMadeList.append(len(engyCiteDict[patent][2]))
    claimsList.append(engyCiteDict[patent][0][1])
    grantYrList.append(engyCiteDict[patent][0][2])

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

    # determine if patent was from a US corp., US gov., or neither 
    classSubclass = engyCiteDict[patent][0][4] 
    assignee = engyCiteDict[patent][0][3]
    #some patents don't have an assignee value
    if assignee in USDict:
      if USDict[assignee] == 2:
        usCorpList.append(1)
      if USDict[assignee] == 6:
        usGovList.append(1)
    else:
      usCorpList.append(0)
      usGovList.append(0)       
     
    if classSubclass in classDict:
      if classDict[classSubclass] == 'fuel':
        fuelList.append(1)
      else:
        fuelList.append(0)
      if classDict[classSubclass] == 'PV':
        PVList.append(1)
      else:
        PVList.append(0)
      if classDict[classSubclass] == 'wind':
        windList.append(1)
      else:
        windList.append(0)
    else:
      fuelList.append(0)
      PVList.append(0)
      windList.append(0)


  # order of values is mean, med, SD, Min, Max   
  citeRecValues[0] = average(citeRecList)
  citeRecValues[1] = median(citeRecList)
  citeRecValues[2] = stdDev(citeRecList,citeRecValues[0])
  citeRecValues[3] = min(citeRecList)
  citeRecValues[4] = max(citeRecList)

  citeMadeValues[0] = average(citeMadeList)
  citeMadeValues[1] = median(citeMadeList)
  citeMadeValues[2] = stdDev(citeMadeList,citeMadeValues[0])
  citeMadeValues[3] = min(citeMadeList)
  citeMadeValues[4] = max(citeMadeList)

  citeLagValues[0] = average(citeLagList)
  citeLagValues[1] = median(citeLagList)
  citeLagValues[2] = stdDev(citeLagList,citeLagValues[0])
  citeLagValues[3] = min(citeLagList)
  citeLagValues[4] = max(citeLagList)

  claimsValues[0] = average(claimsList) 
  claimsValues[1] = median(claimsList) 
  claimsValues[2] = stdDev(claimsList,claimsValues[0]) 
  claimsValues[3] = min(claimsList) 
  claimsValues[4] = max(claimsList) 

  grantYrValues[0] = average(grantYrList) 
  grantYrValues[1] = median(grantYrList) 
  grantYrValues[2] = stdDev(grantYrList,grantYrValues[0]) 
  grantYrValues[3] = min(grantYrList) 
  grantYrValues[4] = max(grantYrList) 

  fuel[0] = average(fuelList)
  fuel[1] = '\t'
  fuel[2] = stdDev(fuelList,fuel[0])

  PV[0] = average(PVList)
  PV[1] = '\t'
  PV[2] = stdDev(PVList,PV[0])

  wind[0] = average(windList)
  wind[1] = '\t'
  wind[2] = stdDev(windList,wind[0])

  usGov[0] = average(usGovList)
  usGov[1] = '\t'
  usGov[2] = stdDev(usGovList,usGov[0])

  usCorp[0] = average(usCorpList)
  usCorp[1] = '\t'
  usCorp[2] = stdDev(usCorpList,usCorp[0])
 
  header = 'Variable' + '\t' + 'Mean' + '\t' + 'Median' + '\t' + 'Std. dev.' + '\t' + 'Min' + '\t' + 'Max'
  print(header)
  outputData = [('Citations received',citeRecValues),('Citations made',citeMadeValues), \
                ('Citation lag',citeLagValues),('Claims made', claimsValues), \
                ('Grant year',grantYrValues),('US corp.',usCorp),('US govt.',usGov), \
                ('Fuel Cells',fuel),('PV',PV),('Wind',wind)]
  outputAnalytics(outputData)

def getCitations(filename,patentList):
  citationFile = open(filename, 'r')
  citationDict = {} 

  for i in range(len(patentList)):
    # 3rd parameter list is citations received, 4th parameter is citations made
    patentID,patentValues = patentList[i][0],[patentList[i][1:],[],[]]
    citationDict[patentID] = patentValues

  # skip header information
  next(citationFile)
  for line in citationFile:
    line = line.rstrip('\n')
    elems = line.split(',')
    #skip the first column in file since it's just a line number
    for i in range(1,len(elems)):
      elems[i] = int(elems[i])
    citingPat,citedPat = elems[1],elems[2]
    # add citation received to associated list and vise veindexrsa
    # 1st column [(0, 7, 1982, 10432905, '136/258'), [], []]
from citationFile is the citing patent, 2nd is the cited patent
    if citingPat in citationDict:
      citationDict[citingPat][2].append(citedPat)
    if citedPat in citationDict:
      citationDict[citedPat][1].append(citingPat)
  return citationDict 

def getPatentData(patFilename,ascFilename):
  inputPatFile = open(patFilename, 'r')
  inputAscFile = open(ascFilename, 'r')
  patentIDs = {}
  patentGrantDict = {}
  patentData = []

  for line in inputPatFile:
    line = line.rstrip('\n')   
    ID = int(line)
    #value is irrelevant, just using dict for speed
    patentIDs[ID] = 0 

  #skip header information
  next(inputAscFile)
  for line in inputAscFile:
    patentInfo = ()
    line = line.rstrip('\n')
    elems = line.split('\t')
    numClaims,grantYear,patentNum,numCites,assignee = 0,0,0,0,0
    classSubclass = elems[6].strip('"')
    if '' != elems[0]:  
      numCites = int(elems[0])
    if '' != elems[11]:  
      grantYear = int(elems[11])
    if '' != elems[17]:  
      numClaims = int(elems[17])
    if '' != elems[20]:  
      patentNum = int(elems[20])
    if '' != elems[21]:
      assignee = int(elems[21])
    if patentNum in patentIDs:
      patentInfo = (patentNum,numCites,numClaims,grantYear,assignee,classSubclass)
      patentData.append(patentInfo)
    patentGrantDict[patentNum] = grantYear
  inputPatFile.close()
  inputAscFile.close()
  return patentGrantDict, sorted(list(set(patentData)))

#assumes patents haven't been filtered based on Nemet's backword/forward citation restrictions 
def citeFilter(citeDict,patList):
  for (patent,a,b,grantYr,d,e) in patList:
    if patent in citeDict:
      if grantYr < 1981 or grantYr > 1996:
        citeDict.pop(patent,None)
  return citeDict

def getEnergyDict(classSubclassFilename):
  classFile = open(classSubclassFilename, 'r')
  energyClassDict = {}
  classCategory = '' 
  
  for line in classFile:
    line = line.rstrip('\n') 
    if '/' not in line:
      classCategory = line
    else:
      classSubclass = line
      energyClassDict[classSubclass] = classCategory
  classFile.close 
  return energyClassDict

def getUSDict(assigneeFilename):
  assigneeFile = open(assigneeFilename,'r')
  USDict = {}

  next(assigneeFile)
  for line in assigneeFile:
    line = line.rstrip('\n') 
    elems = line.split('\t')
    pdpass = int(elems[1])
    elems[0] = elems[0].strip('"')
    # COD is the assignee type
    COD = elems[0].split(" ")
    CODNum = 0
    # 2 is US Corporation, 6 is US government
    if '02' == COD[0] or '06' == COD[0]:
      CODNum = int(COD[0])  
    # all other assignee's COD will be set to 0 since we aren't interested in them
    USDict[pdpass] = CODNum
  assigneeFile.close
  return USDict

def main(argv):
  citationFile = ''
  classSubclassFile = ''
  patentListFile = ''
  completePatDataFile = ''
  assigneeFile = ''
 
  if len(argv) == 0:
    sys.stderr.write('getAnalytics.py -i <input patent file> -c <citation file> -a <complete pat76-06 file> -d <assignee file> -s <energy class/subclass file>\n')
    sys.exit(2)
  try:
    opts,args = getopt.getopt(argv,"hc:i:a:s:d:")
  except getopt.GetoptError:
    sys.stderr.write('getAnalytics.py -i <input patent file> -c <citation file> -a <complete pat76-06 file> -d <assignee file> -s <energy class/subclass file>\n')
    sys.exit(2)
  for opt,arg in opts:
    if opt == '-h':
      print('getAnalytics.py -i <input patent file> -c <citation file> -a <complete pat76-06 file> -d <assignee file> -s <energy class/subclass file>')
      sys.exit()
    elif opt == '-c':
      citationFile = arg
    elif opt == '-i':
      patentListFile = arg      
    elif opt == '-a':
      completePatDataFile = arg      
    elif opt == '-s':
      classSubclassFile = arg
    elif opt == '-d':
      assigneeFile = arg

  completePatDict, energyPatentList = getPatentData(patentListFile,completePatDataFile)
  energyPatDict = getCitations(citationFile,energyPatentList)
  energyClassDict = getEnergyDict(classSubclassFile)
  assigneeDict = getUSDict(assigneeFile) 
  filteredCiteDict = citeFilter(energyPatDict,energyPatentList)
  getCalculations(completePatDict,filteredCiteDict,energyClassDict,assigneeDict)
  
  pkl_file = open('pickle/filter_cite.pkl','wb')
  pickle.dump(filteredCiteDict, pkl_file)
  pkl_file.close()

  # pickling completePatDict, fileteredCiteDict, energuClassDct,assignedDict
  pkl_file = open('pickle/cpd_fcd_ecd_ad.pkl','wb')
  pickle.dump(completePatDict, pkl_file)
  pickle.dump(filteredCiteDict, pkl_file)
  pickle.dump(energyClassDict, pkl_file)
  pickle.dump(assigneeDict, pkl_file)
  pkl_file.close()

  # citingpatent2 = citedPatent
  c = csv.writer(open("filter_cites.csv", 'w'))
  c.writerow(['','citing','cited','ncites7606'])

  count=1

  for key in filteredCiteDict.keys():
    citesReceived = filteredCiteDict[key][1]
    citesMade = filteredCiteDict[key][2]
    for patent in citesReceived:
      c.writerow([count,patent,key,len(citesReceived)])
      count += 1

    for patent in citesMade:
      c.writerow([count,key,patent,len(citesMade)])
      count += 1



  getCitationsWithin10Yrs(completePatDict,filteredCiteDict)

if __name__ == '__main__':
  main(sys.argv[1:])
