# a simple test for a kalman filter
# requires the module pykalmn (install with: sudo pip install pykalman)

import numpy as np
import pykalman
from matplotlib import pyplot as plt
from typing import List

init_x, init_y = 2, 1
init_vx, init_vy = 0, 0

a_x, a_y = .1, .2

n_measures = 100
stdev = 10.0


# compute actual position at time t
def s(t: float) -> List[float]:
    return [init_x + init_vx * t + a_x * t ** 2, init_y + init_vy * t + a_y * t ** 2]

if __name__ == '__main__':
    # the state is a vector (x, y, vx, vy) where vx and vy are the velocity of the moving object in x and y direction

    # transition matrix for future predictions, can be derived from newtonian equations
    F = [[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]]
    # the observation matrix
    Q = [[1, 0, 0, 0], [0, 1, 0, 0]]

    # set up parameters for the kalman filter
    init_state = [init_x, init_y, init_vx, init_vy]  # the inital state of the object to be tracked.
    init_covar = 1.0e-3 * np.eye(4)  # the inital covariance matrix
    transition_cov = 1.0e-4 * np.eye(4)  # the transition covariance
    observation_cov = 1.0e-1 * np.eye(2)  # the observation covariances

    # create the kalman filter
    kf = pykalman.KalmanFilter(
        transition_matrices=F,
        observation_matrices=Q,
        initial_state_mean=init_state,
        initial_state_covariance=init_covar,
        transition_covariance=transition_cov,
        observation_covariance=observation_cov)

    actuals = []  # collect all actual positions of the object to be tracked
    measures = []  # collect all measured positions
    filtered = []  # collect all positions filtered by the Kalman Filter

    last_mean = init_state
    last_covar = init_covar

    # simulate measurements for some time steps
    for t in range(n_measures):
        actual = s(t)
        measured = np.random.normal(s(t), stdev, 2)
        last_mean, last_covar = kf.filter_update(last_mean, last_covar, measured)  # update mean and covariance
        print('\nState at time {} (actual={}, measured={}):\n {}\n {}'.format(t, actual, measured, last_mean, last_covar))

        actuals.append(actual)
        measures.append(measured)
        filtered.append(last_mean[0:2])

    # plot the result
    plt.plot([m[0] for m in measures], [m[1] for m in measures], 'xr', label='measured positions')
    #plt.axis([0,520,360,0])
    #plt.hold(True)
    plt.plot([f[0] for f in filtered], [f[1] for f in filtered], 'ob', label='kalman output')
    #plt.hold(True)
    plt.plot([a[0] for a in actuals], [a[1] for a in actuals], '+g', label='actual positions')

    plt.legend(loc=3)
    plt.title("Constant Acceleration Kalman Filter")
    plt.show()

