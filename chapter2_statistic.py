import sys
sys.path.append('library')

from thinkbayes2 import Suite

class Monty(Suite):
    def __init__(self, obj):
        super().__init__(obj)

    def Likelihood(self, data, hypo):
        """
        Using data likelihood to sample from hypothesis
        Refer to book description in page 7-8 of "think bayes"
        """
        if hypo == data:    
            # if open door 'data' == 'hypo', it's impossible to keep "open door `data`, and car isn't behind door `data`" as True => must False
            return 0
        elif hypo == 'A':
            # if car is actually behind door 'A', then "open door `data`, and car isn't behind door `data`" will be 1/2 True
            return 0.5
        else:
            # if car NOT behind door 'A' and open door 'data'!='hypo', then you can't see car is behind door 'data', when opening door 'data' => must True
            return 1

class M_and_M(Suite):
    def __init__(self, obj):
        """
        __init__ to instantiate AB probablity of A and B hypothesis.
        """
        super().__init__(obj)
        """
        Map from hypothesis (A or B) to probability.
        """
        mix94 = dict(brown=30,
                     yellow=20,
                     red=20,
                     green=10,
                     orange=10,
                     tan=10,
                     blue=0)

        mix96 = dict(blue=24,
                     green=20,
                     orange=16,
                     yellow=14,
                     red=13,
                     brown=13,
                     tan=0)

        hypoA = dict(bag1=mix94, bag2=mix96)
        hypoB = dict(bag1=mix96, bag2=mix94)
        self.hypotheses = dict(A=hypoA, B=hypoB)
    
    def Likelihood(self, data, hypo):
        """
        data is a tuple (bag, color), bag is categorized by year.
        """
        bag, color = data
        mix = self.hypotheses[hypo][bag]
        like = mix[color]
        return like

if __name__ == '__main__':
    # Monty hall
    suite = Monty('ABC')
    suite.Update('B')
    suite.Print()
    # M & M
    suite = M_and_M('AB')
    suite.Update(('bag1', 'yellow'))
    suite.Update(('bag2', 'green'))
    suite.Print()
    
