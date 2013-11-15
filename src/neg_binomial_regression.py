import numpy as np
from scipy.stats import nbinom

def _ll_nb2(y, X, beta, alph):
     mu = np.exp(np.dot(X, beta))
     size = 1 / alph
     prob = size / (size + mu)
     ll = nbinom.logpmf(y, size, prob)
     return ll


from statsmodels.base.model import GenericLikelihoodModel
class NBin(GenericLikelihoodModel):
  def __init__(self, endog, exog, **kwds):
    super(NBin, self).__init__(endog, exog, **kwds)
   
  def nloglikeobs(self, params):
    alph = params[-1]
    beta = params[:-1]
    ll = _ll_nb2(self.endog, self.exog, beta, alph)
    return -ll
  
  def fit(self, start_params=None, maxiter=10000, maxfun=5000, **kwds):
    if start_params == None:
    # Reasonable starting values
      start_params = np.append(np.zeros(self.exog.shape[1]), .5)
      start_params[0] = np.log(self.endog.mean())
      return super(NBin, self).fit(start_params=start_params,maxiter=maxiter, maxfun=maxfun,**kwds)

