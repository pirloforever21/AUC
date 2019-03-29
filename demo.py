'''
Implement following algorithms:
    SAUC
    OAM

Author: Zhenhuan(Neyo) Yang
'''

import h5py
from matplotlib import pyplot as plt
from math import fabs
import SAUC
import OAM

def split(folder,folders):

    '''
    Split the dataset by indices

    input:
        folder - current folder
        folders - number of folders

    output:
        train_list -
        test_list -
    '''

    if folder >= folders:
        print('Exceed maximum folders!')
        return

    # regular portion of each folder
    portion = round(n / folders)
    start = portion * folder
    stop = portion * (folder + 1)

    if folders == 1:
        train_list = [i for i in range(n)]
        test_list = [i for i in range(n)]

    elif folders == 2:
        if folder == 0:
            train_list = [i for i in range(start)] + [i for i in range(stop, n)]
            test_list = [i for i in range(start, stop)]
        else:
            train_list = [i for i in range(start)]
            test_list = [i for i in range(start, n)]

    else:
        if fabs(stop - n) < portion:  # remainder occurs
            train_list = [i for i in range(start)]
            test_list = [i for i in range(start, n)]
        else:
            train_list = [i for i in range(start)] + [i for i in range(stop, n)]
            test_list = [i for i in range(start, stop)]

    return train_list, test_list

if __name__ == '__main__':

    # Read data from hdf5 file
    dataset = 'mnist'
    hf = h5py.File('/Users/yangzhenhuan/PycharmProjects/AUC/datasets/%s.h5' % (dataset), 'r')
    FEATURES = hf['FEATURES'][:]
    LABELS = hf['LABELS'][:]
    hf.close()

    # Define hyper parameters
    N = 3
    T = 200
    folders = 2
    stamp = 10
    iteration = list(range(T//stamp))

    # Define model parameters
    L = [1]
    C = [10]
    Np = [100]
    Nn = [100]

    # Define losses and algorithms
    NAME = ['hinge','logistic']
    ALG = ['SAUC','OAM']
    OPTION = ['sequential','gradient']

    # Prepare training and testing
    n = len(LABELS)
    training = [i for i in range(n // 2)]
    testing = [i for i in range(n // 2, n)]

    # Prepare results
    res = {}
    for name in NAME:
        for alg in ALG:
            if alg == 'SAUC':
                res[(name, alg)] = SAUC(T, name, N, L[0], C[0], FEATURES[training], LABELS[training], FEATURES[testing],
                                        LABELS[testing], stamp=stamp)
            else:
                for option in OPTION:
                    res[(name, alg + '_' + option)] = OAM(T, name, option, C[0], Np[0], Nn[0], FEATURES[training],
                                                          LABELS[training], FEATURES[testing], LABELS[testing],
                                                          stamp=stamp)

    # Plot results
    fig = plt.figure()  # create a figure object
    ax1 = fig.add_subplot(2, 1, 1)
    ax1.plot(sauc_time, sauc_auc, label='SAUC')
    ax1.plot(oam_time, oam_auc, label='OAM')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('AUC')
    plt.legend()
    ax2 = fig.add_subplot(2, 1, 2)
    ax2.plot(iteration, sauc_auc, label='SAUC')
    ax2.plot(iteration, oam_auc, label='OAM')
    ax2.set_xlabel('Iteration')
    ax2.set_ylabel('AUC')
    plt.legend()
    plt.show()