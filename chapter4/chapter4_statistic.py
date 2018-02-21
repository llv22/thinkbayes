from __future__ import print_function
import sys
sys.path.append("library")
from thinkbayes2 import Suite, Pmf, Cdf
import thinkplot

# refer to https://github.com/AllenDowney/ThinkBayes2/blob/master/code/chap04soln.ipynb
class ObservableCoin(Suite):
    def __init__(self, prior, y):
        """
        prior: seq or map
        y: probability of accurate measurement
        """
        # super() with prior parameter, refer to https://stackoverflow.com/questions/576169/understanding-python-super-with-init-methods
        super().__init__(prior);
        # equivanlent to super().__init__(prior)
        # Suite.__init__(self, prior);
        self.y = y;
    def Likelihood(self, data, hypo):
        """
        data: outcome of unreliable measurement, either 'H' or 'T'
        hypo: probability of heads, 0-100
        """
        x = hypo / 100
        y = self.y
        if data == 'H':
#             correctly report head and guarantee correctness, or report tail and happend to report incorrectly
            return x * y + (1-x) * (1-y)
        else:
#         report tail and guarantee correctness, or report head and happend to report incorrectly
            return (1-x) * y + x * (1-y)

if __name__ == '__main__':
    prior = range(0, 101)
    suite = ObservableCoin(prior, y=0.9)
    thinkplot.Pdf(suite)
        