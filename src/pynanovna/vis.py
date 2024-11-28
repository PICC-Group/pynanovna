"""
Plotting functions
"""

import logging
import matplotlib.pyplot as plt
import numpy as np


def plot(
    stream: object,
    axis_mode: str = "first",
    fixed_limits: list[float] = None,
    log: bool = True,
):
    """
    Show a magnitude plot from the data.

    Args:
        stream: The data stream to plot.
        axis_mode (str): 'dynamic', 'fixed', or 'first'. Default is 'dynamic'.
            'dynamic' - Axes limits adjust to data.
            'fixed' - Axes limits are fixed as per 'fixed_limits'.
            'first' - Axes limits are set based on the first data batch and kept constant.
        fixed_limits (list): A dictionary containing axis limits if axis_mode is 'fixed'.
            Example: [min_s11, max_s11, min_s21, max_s21]
        log (bool): If the magnitude should be log or not.

    """
    plt.ion()
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    fig.tight_layout(pad=4.0)

    ax[0].set(xlabel="Frequency (Hz)", ylabel="dB", title="S11")
    ax[1].set(xlabel="Frequency (Hz)", ylabel="dB", title="S21")

    (line1,) = ax[0].plot([], [], label="S11")
    (line2,) = ax[1].plot([], [], label="S21")
    ax[0].legend()
    ax[1].legend()

    if log:
        ax[0].set_yscale("log")
        ax[1].set_yscale("log")

    plt.show()

    first_data = True

    try:
        for new_data in stream:
            s11 = np.abs(new_data[0])
            s21 = np.abs(new_data[1])
            x = new_data[2]

            line1.set_data(x, s11)
            line2.set_data(x, s21)

            if first_data:
                if axis_mode == "first" or axis_mode == "fixed":
                    fixed_xlim = (min(x), max(x))
                    fixed_ylim_s11 = (
                        (fixed_limits[0], fixed_limits[1])
                        if axis_mode == "fixed"
                        else (min(s11), max(s11))
                    )
                    fixed_ylim_s21 = (
                        (fixed_limits[2], fixed_limits[3])
                        if axis_mode == "fixed"
                        else (min(s21), max(s21))
                    )

                    ax[0].set_xlim(*fixed_xlim)
                    ax[0].set_ylim(*fixed_ylim_s11)
                    ax[1].set_xlim(*fixed_xlim)
                    ax[1].set_ylim(*fixed_ylim_s21)

                first_data = False

            if axis_mode == "dynamic":
                ax[0].relim()
                ax[0].autoscale_view()
                ax[1].relim()
                ax[1].autoscale_view()

            fig.canvas.draw()
            fig.canvas.flush_events()
            plt.pause(0.001)

    except KeyboardInterrupt:
        logging.info("Killing csv stream because of keyboard interrupt.")
        return
    except Exception as e:
        logging.critical("Error in the magnitude plot function.", exc_info=e)
        return

    plt.ioff()
    plt.show()


def polar(stream: object, normalize: bool = False):
    """
    Create polar plots for S11 and S21 data.

    Args:
        stream: The data stream to plot.
        normalize (bool): If True, normalize the data based on the first value.
    """
    plt.ion()
    fig, ax = plt.subplots(1, 2, subplot_kw=dict(polar=True), figsize=(12, 6))
    fig.tight_layout(pad=4.0)

    (line1,) = ax[0].plot([], [], label="S11")
    (line2,) = ax[1].plot([], [], label="S21")
    ax[0].legend()
    ax[1].legend()
    ax[0].set_title("S11 Polar Plot")
    ax[1].set_title("S21 Polar Plot")

    plt.show()

    first_data = True
    ref_s11, ref_s21, ref_theta1, ref_theta2 = None, None, None, None

    for new_data in stream:
        try:
            s11 = np.abs(new_data[0])
            s21 = np.abs(new_data[1])
            theta1 = np.angle(new_data[0])
            theta2 = np.angle(new_data[1])

            if first_data:
                if normalize:
                    ref_s11, ref_s21 = s11[0], s21[0]
                    ref_theta1, ref_theta2 = theta1[0], theta2[0]

                    s11 = s11 - ref_s11
                    s21 = s21 - ref_s21
                    theta1 = (theta1 - ref_theta1) % (2 * np.pi)
                    theta2 = (theta2 - ref_theta2) % (2 * np.pi)

                ax[0].set_ylim(0, max(s11) * 1.1)
                ax[1].set_ylim(0, max(s21) * 1.1)
                first_data = False

            elif normalize:
                s11 = s11 - ref_s11
                s21 = s21 - ref_s21
                theta1 = (theta1 - ref_theta1) % (2 * np.pi)
                theta2 = (theta2 - ref_theta2) % (2 * np.pi)

            line1.set_data(theta1, s11)
            line2.set_data(theta2, s21)

            fig.canvas.draw()
            fig.canvas.flush_events()
            plt.pause(0.01)

        except KeyboardInterrupt:
            logging.info("Killing csv stream because of keyboard interrupt.")
            return
        except Exception as e:
            logging.critical("Error in the polar plot function.", exc_info=e)
            return

    plt.ioff()
    plt.show()
