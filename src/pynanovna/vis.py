import matplotlib.pyplot as plt
import numpy as np


def plot(vna, animate, data_file=False, loop=False):
    """Show a magnitude plot from the data. If animate is True it will update the plot continuously with data from live stream or previously recorded file.

    Args:
        animate (bool): If the stream should be from a single sweep or continuous stream.
        data_file (bool, str): Pass a filepath to show previously recorded stream. Defaults to False.
        loop (bool): Loop the stream from the datafile. Defaults to False.
    """
    if animate:
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
        run = True
        while run:
            data = vna.stream_data(data_file)
            for new_data in data:
                s11 = vna.magnitude(new_data[0], new_data[1])
                s21 = vna.magnitude(new_data[2], new_data[3])
                x = new_data[4]
                line1.set_data(x, s11)
                line2.set_data(x, s21)

                # Update limits and redraw the plot
                for ax_item in ax.flat:
                    ax_item.relim()  # Recalculate limits
                    ax_item.autoscale_view()  # Autoscale

                fig.canvas.draw()
                fig.canvas.flush_events()
                plt.pause(0.01)
            run = data_file and loop
            if vna.verbose:
                print("Looped the animation.")

    else:
        if vna.playback_mode:
            print(
                "Cannot run sweeps in playback mode. Connect NanoVNA and restart."
            )
            return
        data = vna.single_sweep()
        magnitudeS11 = vna.magnitude(data[0], data[1])
        magnitudeS21 = vna.magnitude(data[2], data[3])
        x = data[4]
        y1 = magnitudeS11
        y2 = magnitudeS21

        fig, ax = plt.subplots(2, 1)
        fig.tight_layout(pad=4.0)

        # plot 1
        ax[0].plot(x, y1, label="S11")
        ax[0].legend()

        # plot 2
        ax[1].plot(x, y2, label="S21")
        ax[1].legend()

        for ax in ax.flat:
            ax.set(xlabel="Frequency (Hz)", ylabel="dB")

        plt.show()

def plot_polar(vna, animate, data_file=False, loop=False):
    """Show a magnitude plot from the data. If animate is True it will update the plot continuously with data from live stream or previously recorded file.

    Args:
        animate (bool): If the stream should be from a single sweep or continuous stream.
        data_file (bool, str): Pass a filepath to show previously recorded stream. Defaults to False.
        loop (bool): Loop the stream from the datafile. Defaults to False.
    """
    if animate:
        plt.ion()
        fig, ax = plt.subplots(2, 1)
        fig.tight_layout(pad=4.0)

        # Set labels for each subplot
        for ax_item in ax.flat:
            ax_item.set(xlabel="Frequency (Hz)", ylabel="dB")

        # Initialize lines for each subplot
        #(line1,) = ax[0].plot([], [], label="S11")
        #(line2,) = ax[1].plot([], [], label="S21")

        sc1 = ax[0].scatter([], [], label="S11")
        sc2 = ax[1].scatter([], [], label="S21")

        # Display legend for each subplot
        ax[0].legend()
        ax[1].legend()
        plt.show()
        run = True
        while run:
            data = vna.stream_data(data_file)
            for new_data in data:
                #s11 = vna.magnitude(new_data[0], new_data[1])
                #s21 = vna.magnitude(new_data[2], new_data[3])
                #x = new_data[4]
                #line1.set_data(x, s11)
                #line2.set_data(x, s21)
                r1 = np.sqrt(new_data[0]**2 + new_data[1]**2)
                theta1 = np.arctan2(new_data[1], new_data[0])
                r2 = np.sqrt(new_data[0]**2 + new_data[1]**2)
                theta2 = np.arctan2(new_data[1], new_data[0])

                sc1.set_data(r1, theta1)
                sc2.set_data(r2, theta2)

                # Update limits and redraw the plot
                #for ax_item in ax.flat:
                #    ax_item.relim()  # Recalculate limits
                #    ax_item.autoscale_view()  # Autoscale

                fig.canvas.draw()
                fig.canvas.flush_events()
                plt.pause(0.01)
            run = data_file and loop
            if vna.verbose:
                print("Looped the animation.")

    else:
        if vna.playback_mode:
            print(
                "Cannot run sweeps in playback mode. Connect NanoVNA and restart."
            )
            return
        data = vna.single_sweep()
        magnitudeS11 = vna.magnitude(data[0], data[1])
        magnitudeS21 = vna.magnitude(data[2], data[3])
        x = data[4]
        y1 = magnitudeS11
        y2 = magnitudeS21

        fig, ax = plt.subplots(2, 1)
        fig.tight_layout(pad=4.0)

        # plot 1
        ax[0].plot(x, y1, label="S11")
        ax[0].legend()

        # plot 2
        ax[1].plot(x, y2, label="S21")
        ax[1].legend()

        for ax in ax.flat:
            ax.set(xlabel="Frequency (Hz)", ylabel="dB")

        plt.show()

    # Convert re, im to polar coordinates (magnitude r and angle theta)
    r = np.sqrt(re**2 + im**2)
    theta = np.arctan2(im, re)

    # Create a polar plot
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.scatter(theta, r)

    # Add title and labels
    ax.set_title('Polar Plot from Real and Imaginary Components')
    ax.set_xlabel('Angle (radians)')
    ax.set_ylabel('Radius')