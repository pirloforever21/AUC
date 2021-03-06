'''
Show results
Author: Zhenhuan(Neyo) Yang
'''

import pandas as pd
import numpy as np
from itertools import product
import matplotlib.pyplot as plt
from math import fabs

def lookat(algs,datasets,para):
    '''
    look at results
    input:
        alg - algorithm
        dataset -
        para - which result you want to see
    output:
        fig -
    '''

    # result = pd.DataFrame()
    for dataset in datasets:

        for alg in algs:

            print('alg = %s data = %s' % (alg, dataset))

            if para == 'cv':

                # Read
                df = pd.read_pickle('/home/neyo/PycharmProjects/AUC/results/cv_%s_%s.h5' % (alg, dataset))

                for column in df.columns:
                    ind = np.argmax(df[column]['MEAN'])
                    last1 = df[column]['MEAN'][-1]
                    last2 = df[column]['MEAN'][-2]

                    if fabs(last1 - last2) > .1 or ind < 1:
                        pass
                    else:
                        print('c = %.2f R = %.2f AUC = ' % (column[0], column[1]), end=' ')
                        print(('%.4f$\pm$' % df[column]['MEAN'][ind]).lstrip('0'), end='')
                        print(('%.4f' % df[column]['STD'][ind]).lstrip('0'))

                        plt.plot(df[column]['MEAN'], label='c= %.2f R = %.2f AUC = %.4f$\pm$%.4f$'
                                                           % (column[0], column[1], df[column]['MEAN'][ind],
                                                              df[column]['STD'][ind]))

                plt.xlabel('Iteration')
                plt.ylabel('AUC')
                plt.ylim([.5, 1])
                plt.legend( prop={'size': 6})
                plt.title('%s_%s' % (alg, dataset))
                plt.show()

            elif para == 'bern':

                # Read
                df = pd.read_pickle('/home/neyo/PycharmProjects/AUC/results/deg_%s.h5' % (dataset))

                # results
                line = []
                error = []
                for m in df.columns:
                    ind = np.argmax(df[m]['MEAN'])
                    line.append(df[m]['MEAN'][ind])
                    error.append(df[m]['STD'][ind])
                plt.style.use('seaborn-whitegrid')
                plt.errorbar(df.columns, line, yerr=error, fmt='--o', capsize=5)

                plt.xlabel('Degree')
                plt.ylabel('AUC')
                plt.ylim([.5, 1])
                plt.xticks(df.columns)
                plt.title('%s' % (dataset))
                plt.show()


            else:
                print('Wrong parameter!')
                return

    return

if __name__ == '__main__':

    algs = ['SAUC','OAM']
    datasets = ['sector.scale']
    para = 'cp'

    lookat(algs,datasets,para)