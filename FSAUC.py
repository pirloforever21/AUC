'''
Fast Stochastic Maximization with O(1/n)-Convergence Rate by Liu et al
Author: Zhenhuan(Neyo) Yang
Date: 4/14/19
'''

import numpy as np
import time
from math import sqrt,log,floor,fabs
from sklearn.metrics import roc_auc_score

def proj_sim(v,R):
    '''
    projection onto simplex by Duchi et al.
    input:
        v -
        R - radius
    output:
        w -
    '''

    # compute l1 norm
    norm = np.linalg.norm(v,ord=1)

    if norm <= R:
        w = v
    else:
        u = np.sort(np.abs(v))[::-1] # sort in descending order
        sv = np.cumsum(u) # sum one by one
        rho = np.nonzero(u * np.arange(1, len(v) + 1) > (sv - R))[0][-1]
        theta = (sv[rho] - R) / (rho + 1)
        w = np.sign(v) * np.maximum(np.abs(v) - theta, 0)

    return w

def proj_l2(v,o,R):
    '''
    Projection onto eccentric l2 ball
    input:
        v -
        o - center
        R - radius
    output:
        w - projected
    '''

    norm = np.linalg.norm(v-o)

    if norm <= R:
        w = v
    else:
        w = v / norm * R + o

    return w


def proj_primal(w,a,b,o,r,R,kappa):
    '''
    Alternating Projection Algorithm
    input:
        v -
        R - radius
    output:
        w -
    '''

    d = len(w)

    # Do it twice!
    # l1 projection
    w = proj_sim(w, R)
    a = np.sign(a) * min(fabs(a), R * kappa)
    b = np.sign(b) * min(fabs(b), R * kappa)

    # l2 projection
    v = np.append(w, a)
    v = np.append(v, b)
    v = proj_l2(v, o, r)

    w = v[:d] + 0.0
    a = v[d] + 0.0
    b = v[d + 1] + 0.0

    # l1 projection
    w = proj_sim(w, R)
    a = np.sign(a) * min(fabs(a), R * kappa)
    b = np.sign(b) * min(fabs(b), R * kappa)

    # l2 projection
    v = np.append(w, a)
    v = np.append(v, b)
    v = proj_l2(v, o, r)

    w = v[:d] + 0.0
    a = v[d] + 0.0
    b = v[d + 1] + 0.0

    return w,a,b

def proj_dual(alpha,o,D,R,kappa):
    '''
    Alternate projection
    '''

    # Do it twice!
    alpha = np.sign(alpha) * min(fabs(alpha), 2 * R * kappa)

    alpha = proj_l2(alpha,o,D)

    alpha = np.sign(alpha) * min(fabs(alpha), 2 * R * kappa)

    alpha = proj_l2(alpha, o, D)

    return alpha

def FSAUC(Xtr,Xte,Ytr,Yte,options,stamp=10):
    '''
    Fast Stochastic AUC Maximization
    input:
        n - total iteration
        Xtr -
        Ytr -
        Xte -
        Yte -
        options -
    output:
        Wt -
    '''

    # load parameter
    R = options['R']
    c = options['c']
    delta = options['delta']
    n = options['T']

    print('FSAUC with R = %.2f c = %.2f delta = %.2f' % (R, c, delta))

    # normalized data
    # kappa = max(np.linalg.norm(Xtr, axis=1))
    kappa = 1

    # get the dimension of what we are working with
    N, d = Xtr.shape

    # set
    log2 = lambda x: log(x) / log(2)
    m = floor(log2(2 * n / log2(n)) / 2) - 1
    n0 = floor(n / m)
    r = 2 * sqrt(1 + 2 * kappa ** 2) * R  # R0
    G = max((1 + 4 * kappa) * kappa * (R + 1), 2 * kappa * (2 * R + 1 + 2 * R * kappa),
            2 * kappa * (4 * kappa * R + 11 * R + 1)) * c
    beta = (1 + 8 * kappa ** 2)
    D = 2 * sqrt(2) * kappa * r

    # initialize
    Wt = np.zeros(d)
    At = 0.0
    Bt = 0.0
    ALPHAt = 0.0

    # record auc
    roc_auc = []

    # record time elapsed
    elapsed_time = []
    start_time = time.time()

    for k in range(m):

        # initialize counts
        Ap = np.zeros(d)  # just d dim as last two dim is always zero
        Am = np.zeros(d)
        Tp = 0
        Tm = 0
        pt = 0

        wt = Wt + 0.0
        at = At + 0.0
        bt = Bt + 0.0
        alphat = ALPHAt + 0.0

        Vt = np.append(Wt, At)
        Vt = np.append(Vt, Bt)

        WT = wt + 0.0
        AT = at + 0.0
        BT = bt + 0.0

        # step size
        eta = sqrt(beta) / (sqrt(3 * n0) * G) * r

        # Primal Dual Stochastic Gradient(PDSG)
        for t in range(1,n0+1):

            # compute inner product
            prod = np.inner(wt, Xtr[(k*n0+t)%N])

            if Ytr[(k*n0+t)%N] == 1:
                Ap += Xtr[(k*n0+t)%N]
                Tp += 1
                pt = Tp / (Tp+Tm)

                # compute gradient
                gradwt = 2 * (1 - pt) * (prod - at) - 2 * (1 + alphat) * (1 - pt) # no xt yet!
                gradat = 2 * (1 - pt) * (at - prod)
                gradbt = 0.0
                gradalphat = -2 * (1 - pt) * prod - 2 * pt * (1-pt) * alphat

            else:
                Am += Xtr[(k * n0 + t) % N]
                Tm += 1
                pt = Tp / (Tp + Tm)

                # compute gradient
                Ap += Xtr[(k * n0 + t) % N]
                Tp += 1
                pt = Tp / (Tp + Tm)

                # compute gradient
                gradwt = 2 * pt * (prod - bt) + 2 * (1 + alphat) * pt # no xt yet!
                gradat = 0.0
                gradbt = 2 * pt * (bt - prod)
                gradalphat = 2 * pt * prod - 2 * pt * (1-pt) * alphat

            # update variable
            wt = wt - eta * gradwt * Xtr[(k*n0+t)%N]
            at = at - eta * gradat
            bt = bt - eta * gradbt
            alphat = alphat + eta * gradalphat

            # projection
            wt, at, bt = proj_primal(wt, at, bt, Vt, r, R, kappa)
            alphat = proj_dual(alphat, ALPHAt, D, R, kappa)

            WT = (t*WT + wt) / (t+1)
            AT = (t * AT + at) / (t + 1)
            BT = (t * BT + bt) / (t + 1)

            # write results
            elapsed_time.append(time.time() - start_time)
            roc_auc.append(roc_auc_score(Yte, np.dot(Xte, WT)))

            # running log
            if (k * n0 + t) % stamp == 0:
                print('iteration: %d AUC: %.6f time eplapsed: %.2f' % (k * n0 + t, roc_auc[-1], elapsed_time[-1]))

        # update
        Wt = WT + 0.0
        At = AT + 0.0
        Bt = BT + 0.0
        ALPHAt = np.inner(Am / Tm - Ap / Tp, WT)

        # lemma has flaw
        r = r / 2
        temp = min(pt, 1 - pt) * n0 - sqrt(2 * n0 * log(12 / delta))
        if temp>0:
            D = 2 * sqrt(2) * kappa * r + 4 * sqrt(2) * kappa * (2 + sqrt(2 * log(12 / delta))) * (1 + 2 * kappa) * R / sqrt(temp)
        else:
            D = 1e7

        temp = min(pt, 1 - pt) - sqrt(2 * log(12 / delta) / n0)
        if temp > 0:
            beta = (1 + 8 * kappa ** 2) + 32 * kappa ** 2 * (1 + 2 * kappa) ** 2 * (2 + sqrt(2 * log(12 / delta))) ** 2 / (temp)
        else:
            beta = 1e7

    return elapsed_time, roc_auc






def proj_l1(v,R):
    '''
    Projection onto l1 ball by Duchi et al
    input:
        v - vector
        R - radius
    output:
        w - projected
    '''

    n = len(v)

    # initialize
    U = list(range(n))
    s = 0
    rho = 0

    # update
    while U:
        k = np.random.choice(U)
        # partition
        G = [j for j in U if v[j]>=v[k]]
        L = [j for j in U if v[j]<v[k]]

        # calculate
        delta_rho = len(G)
        delta_s = sum(v[G])

        if (s+delta_s) - (rho+delta_rho)*v[k] < R:
            s += delta_s
            rho += delta_rho
            U = L + []
        else:
            U = G.pop(k)

    # set
    theta = (s-R)/rho

    # output
    w = np.maximum(v - theta,0)

    return w

def alt_proj_dual(alpha, o, D, R, kappa):
    '''
    Alternate projection
    '''

    l1alpha = fabs(alpha)
    l2alpha = np.linalg.norm(alpha-o)

    while l1alpha>2*R*kappa and l2alpha>D:
        alpha = 2*R*kappa
        alpha = proj_l2(alpha,o,D)

        l1alpha = fabs(alpha)
        l2alpha = np.linalg.norm(alpha-o)

    return alpha

def alt_proj_primal(w,a,b,o,r,R,kappa):
    '''
    Alternating Projection Algorithm
    input:
        v -
        R - radius
    output:
        w -
    '''

    d = len(w)

    l1w = np.linalg.norm(w,ord=1)
    l1a = fabs(a)
    l1b = fabs(b)
    v = np.append(w,a)
    v = np.append(v,b)
    l2v = np.linalg.norm(v-o)

    while l1w>R and l1a>R*kappa and l1b>R*kappa and l2v>r:
        w = proj_sim(w,R)
        a = R*kappa
        b = R*kappa
        v = np.append(w, a)
        v = np.append(v, b)
        v = proj_l2(v,o,r)

        w = v[:d] + 0.0
        a = v[d] + 0.0
        b = v[d+1] + 0.0

        l1w = np.linalg.norm(w, ord=1)
        l1a = fabs(a)
        l1b = fabs(b)
        v = np.append(w, a)
        v = np.append(v, b)
        l2v = np.linalg.norm(v - o)

    return w, a, b