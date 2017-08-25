import numpy as np
import pykalman
from typing import Optional


class PositionKalmanFilter(object):
    """
    A class that implements a kalman filter for a moving object in a 2D cathesian space.
    Basically a wrapper around pykalman.
    """

    def __init__(self, init_state: Optional[np.array] =None):
        """
        Create a new Kalman Filter.

        :param init_state: the initial state of the object to track. Will be the zero vector if set to None.
        """

        object.__init__(self)

        self.__state = init_state if init_state is not None else np.zeros(shape=(4,))
        self.__covar = np.eye(4) * 1e-3
        self.__transition_covar = np.eye(4) * 1e-4
        self.__observation_covar = np.eye(2) * 1e-1 + np.random.randn(2, 2) * 1e-1

        transition_matrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]])
        observation_matrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]])

        self.__internal_filter = pykalman.KalmanFilter(
            transition_matrices=transition_matrix,
            observation_matrices=observation_matrix,
            initial_state_mean=self.__state,
            initial_state_covariance=self.__covar,
            transition_covariance=self.__transition_covar,
            observation_covariance=self.__observation_covar
        )

    def filter_update(self, observation: np.array) -> np.array:
        """
        Filters the given observation, returns the filtered value and updates the internal filter accordingly
        :param observation: the observation that was made, should be a 2-dimensional array
        :return: the filtered observation as a 2-dimensional numpy array
        """

        self.__state, self.__covar = self.__internal_filter.filter_update(self.__state, self.__covar, observation)
        return self.__state[0:2]  # return the position part of the state vector


class ScalarKalmanFilter(object):
    """
    A class that implements a kalman filter for a single scalar value, e.g. a sensor value
    """

    def __init__(self, init_value: float =0.0, process_noise: float =.001, sensor_noise: float =10):
        """
        Create a new Kalman Filter.

        :param init_value: the initial value
        """

        object.__init__(self)

        self.__state = init_value
        self.__error = 1
        self.__process_noise = process_noise
        self.__sensor_noise = sensor_noise
        self.__kalman_gain = 1

    def filter_update(self, observation: float) -> float:
        """
        Filters the given observation, returns the filtered value and updates the internal filter accordingly
        :param observation: the observation that was made
        :return: the filtered observation
        """

        # predict
        self.__error = self.__error + self.__process_noise

        # update
        self.__kalman_gain = self.__error / (self.__error + self.__process_noise)
        self.__state = self.__state + self.__kalman_gain * (observation - self.__state)
        self.__error = (1 - self.__kalman_gain) * self.__process_noise

        return self.__state


# execute some test demonstration if this module is run as main
if __name__ == '__main__':
    from matplotlib import pyplot as plt

    a_x, a_y = 0.01, 0.02  # acceleration
    n_measures = 100

    def s(t: float) -> np.array:
        return np.array([t + a_x * t ** 2, a_y * t ** 2])

    kf = PositionKalmanFilter()

    # collect actual, measured and filtered values for latter plotting
    actuals = []
    measures = []
    filtered = []

    # simulate measurements for some time steps
    for t in range(n_measures):
        actual = s(t)
        measured = np.random.normal(s(t), 5, 2)
        kf_filtered = kf.filter_update(measured)
        print('t={}: actual={}, measured={}, filtered={}'.format(t, actual, measured, kf_filtered))

        actuals.append(actual)
        measures.append(measured)
        filtered.append(kf_filtered)

    # plot the result
    plt.plot([m[0] for m in measures], [m[1] for m in measures], 'xr', label='measured positions')
    plt.plot([f[0] for f in filtered], [f[1] for f in filtered], 'ob', label='kalman output')
    plt.plot([a[0] for a in actuals], [a[1] for a in actuals], '+g', label='actual positions')

    plt.legend(loc=3)
    plt.title('Kalman Filter Application')
    plt.show()

    # do the same for the scalar filter
    def v(t: float) -> np.array:
        return np.array([t + 0.1 * t])

    kf = ScalarKalmanFilter()

    actuals, measures, filtered = [], [], []

    # simulate measurements for some time steps
    for t in range(n_measures):
        actual = v(t)
        measured = np.random.normal(v(t), 5, 1)
        kf_filtered = kf.filter_update(measured)
        print('t={}: actual={}, measured={}, filtered={}'.format(t, actual, measured, kf_filtered))

        actuals.append(actual)
        measures.append(measured)
        filtered.append(kf_filtered)

    # plot the result
    plt.plot(range(n_measures), [m[0] for m in measures], 'xr', label='measured value')
    plt.plot(range(n_measures), [f[0] for f in filtered], 'ob', label='kalman output')
    plt.plot(range(n_measures), [a[0] for a in actuals], '+g', label='actual value')

    plt.legend(loc=3)
    plt.title('Kalman Scalar Filter')
    plt.show()





