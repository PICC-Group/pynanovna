import matplotlib.pyplot as plt
from math import pi


def plot(stream):
    """Show a magnitude plot from the data. If animate is True it will update the plot continuously with data from live stream or previously recorded file.

    Args:
        stream: The data stream to plot.
    """
    plt.ion()
    fig, ax = plt.subplots(2, 1)
    fig.tight_layout(pad=4.0)

    # Set labels for each subplot
    for ax_item in ax.flat:
        ax_item.set(xlabel="Frequency (Hz)", ylabel="dB")

    # Initialize lines for each subplot
    (line1,) = ax[0].plot([], [], label="S11")
    (line2,) = ax[1].plot([], [], label="S21")

    # Display legend for each subplot
    ax[0].legend()
    ax[1].legend()
    plt.show()

    first_data = True
    run = True
    while run:
        try:
            for new_data in stream:
                s11 = [new_data[0][i].gain for i in range(len(new_data[0]))]
                s21 = [new_data[1][i].gain for i in range(len(new_data[1]))]
                x = [new_data[0][i].freq for i in range(len(new_data[0]))]

                line1.set_data(x, s11)
                line2.set_data(x, s21)

                if first_data:
                    # Set the x and y limits based on the first data
                    ax[0].set_xlim(min(x), max(x))
                    ax[0].set_ylim(min(s11) * 2, max(s11) * 0.5)
                    ax[1].set_xlim(min(x), max(x))
                    ax[1].set_ylim(min(s21) * 2, max(s21) * 0.5)
                    first_data = False

                fig.canvas.draw()
                fig.canvas.flush_events()
                plt.pause(0.01)

        except KeyboardInterrupt:
            return
        
        except Exception as e:
            print("Error in plot: ", e)

def polar(stream, normalize=False):
    plt.ion()
    fig, ax = plt.subplots(1, 2, subplot_kw=dict(polar=True))
    fig.tight_layout(pad=4.0)

    # Initialize lines for each subplot
    (line1,) = ax[0].plot([], [], label="S11")
    (line2,) = ax[1].plot([], [], label="S21")

    # Display legend for each subplot
    ax[0].legend()
    ax[1].legend()
    plt.show()

    first_data = True
    first_s11, first_s21, first_phase1, first_phase2 = None, None, None, None
    run = True
    while run:
        try:
            for new_data in stream:
                s11 = [new_data[0][i].gain for i in range(len(new_data[0]))]
                s21 = [new_data[1][i].gain for i in range(len(new_data[1]))]
                theta1 = [new_data[0][i].phase for i in range(len(new_data[0]))]
                theta2 = [new_data[1][i].phase for i in range(len(new_data[1]))]

                if first_data:
                    # Optionally set the radial limits based on the first data
                    ax[0].set_ylim(min(s11) * 10, max(s11) * 10)
                    ax[1].set_ylim(min(s21) * 10, max(s21) * 10)

                    if normalize:
                        first_s11, first_s21 = s11[0], s21[0]
                        first_phase1, first_phase2 = theta1[0], theta2[0]

                        ax[0].set_ylim(min([gain - first_s11 for gain in s11]) * 10, max([gain - first_s11 for gain in s11]) * 10)
                        ax[1].set_ylim(min([gain - first_s21 for gain in s21]) * 10, max([gain - first_s21 for gain in s21]) * 10)

                    first_data = False

                if normalize:
                    s11 = [gain - first_s11 for gain in s11]
                    s21 = [gain - first_s21 for gain in s21]
                    theta1 = [(phase - first_phase1) % (2 * pi) for phase in theta1]
                    theta2 = [(phase - first_phase2) % (2 * pi) for phase in theta2]

                line1.set_data(theta1, s11)
                line2.set_data(theta2, s21)

                fig.canvas.draw()
                fig.canvas.flush_events()
                plt.pause(0.01)

        except KeyboardInterrupt:
            return
        
        except Exception as e:
            print("Error in plot: ", e)