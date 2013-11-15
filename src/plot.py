import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import cPickle as pickle

mu, sigma = 100, 15
x = mu + sigma * np.random.randn(10000) # this has to be changed

y=[]
x=[]

pickled_data = pickle.load(open('graph_dict.pkl','rb'))
index=0.9

for i in range(0,10):
    fwd_citations = pickled_data[i]
    
    print len(fwd_citations)
    avg = 1.0*sum(fwd_citations)/ len(fwd_citations)
    y.append(avg)
    x.append(i*1.0/10)


fig = plt.figure()
ax = fig.add_subplot(111)



print y





ax.plot(x,y,'bo-')
ax.set_xlabel('KL-index')
ax.set_ylabel('Avg # forward Citations')
ax.set_title(r'$\mathrm{KL-index\ vs\ Avg\ forward\ Citation\ Count }$')
ax.set_xlim(0, 1)
ax.set_ylim(0,10)
ax.grid(True)

plt.show()
