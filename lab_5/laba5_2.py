import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy import signal
# ^ Завантаження бібліотек ^


t = np.linspace(0, 10, 1000)

# Дефолтні параметри
default_amplitude = 1
default_frequency = 1
default_phase = 0
default_noise_mean = 0
default_noise_covariance = 0.05
default_show_noise = False
filter_param_default = 0.5

last_noise_mean = default_noise_mean
last_noise_covariance = default_noise_covariance

# Шум
noise = np.random.multivariate_normal([default_noise_mean], [[default_noise_covariance]], len(t))[:,0]

def generate_noise(mean, covariance, length):
    global noise
    noise = np.random.multivariate_normal(mean, covariance, length)[:,0]


# Функція
def harmonic_with_noise(t, amplitude, frequency, phase, noise_mean, noise_covariance, show_noise):
    graph = amplitude * np.sin(2 * np.pi * frequency * t + phase)
    global last_noise_mean
    global last_noise_covariance   
    if show_noise:
        if (noise_mean != last_noise_mean) or (noise_covariance != last_noise_covariance):
            generate_noise(noise_mean, noise_covariance, len(t))
        last_noise_mean = noise_mean
        last_noise_covariance = noise_covariance
        return graph + noise
    else:
        last_noise_mean = noise_mean
        last_noise_covariance = noise_covariance
        return graph
    
# Відфільтрований шум
def harmonic_with_noise_filtered(noised_graph, filter_param):
    b, a = signal.iirfilter(4, filter_param, btype="lowpass")
    filtered_graph = signal.lfilter(b, a, noised_graph)
    return filtered_graph

g_default = harmonic_with_noise(t, default_amplitude, default_frequency, default_phase, default_noise_mean, default_noise_covariance, default_show_noise)
fig, ax = plt.subplots(2, figsize=(12, 8))
line, = ax[0].plot(t, g_default, linewidth=2, color="green")
line2, = ax[1].plot(t, harmonic_with_noise_filtered(g_default, filter_param_default), linewidth=2, color="red")
fig.subplots_adjust(left=0.2, bottom=0.4)


# Слайдери
ax_amplitude = plt.axes([0.2, 0.25, 0.65, 0.03])
ax_frequency = plt.axes([0.2, 0.2, 0.65, 0.03])
ax_phase = plt.axes([0.2, 0.15, 0.65, 0.03])
ax_noise_mean = plt.axes([0.2, 0.1, 0.65, 0.03])
ax_noise_covariance = plt.axes([0.2, 0.05, 0.65, 0.03])
ax_filter_param = plt.axes([0.2, 0.3, 0.65, 0.03])

s_amplitude = Slider(ax_amplitude, "Amplitude", 0.1, 2.0, valinit=default_amplitude)
s_frequency = Slider(ax_frequency, "Frequency", 0.1, 5.0, valinit=default_frequency)
s_phase = Slider(ax_phase, "Phase", 0, 2*np.pi, valinit=default_phase)
s_noise_mean = Slider(ax_noise_mean, "Noise Mean", -1, 1, valinit=default_noise_mean)
s_noise_covariance = Slider(ax_noise_covariance, "Noise Covariance", 0.01, 1, valinit=default_noise_covariance)
s_filter_param = Slider(ax_filter_param, "Parameter (for filter)", 0.1, 0.9, valinit=filter_param_default)


# Чекбокс
ax_show_noise = plt.axes([0.025, 0.6, 0.1, 0.05])
check_show_noise = CheckButtons(ax_show_noise, ["Show Noise"], [default_show_noise], label_props={"color": "blue"})


# Update (оновлення параметрів)
def update(val):
    amplitude = s_amplitude.val
    frequency = s_frequency.val
    phase = s_phase.val
    noise_mean = [s_noise_mean.val]
    noise_covariance = [[s_noise_covariance.val]]
    show_noise = check_show_noise.get_status()[0]
    filter_param = s_filter_param.val
    g = harmonic_with_noise(t, amplitude, frequency, phase, noise_mean, noise_covariance, show_noise)
    line.set_ydata(g)
    line2.set_ydata(harmonic_with_noise_filtered(g, filter_param))
    fig.canvas.draw_idle()

s_amplitude.on_changed(update)
s_frequency.on_changed(update)
s_phase.on_changed(update)
s_noise_mean.on_changed(update)
s_noise_covariance.on_changed(update)
check_show_noise.on_clicked(update)
s_filter_param.on_changed(update)


# Reset (скидання параметрів)
def reset(event):
    s_amplitude.reset()
    s_frequency.reset()
    s_phase.reset()
    s_noise_mean.reset()
    s_noise_covariance.reset()
    s_filter_param.reset()

button_reset_ax = plt.axes([0.025, 0.65, 0.1, 0.05])
button_reset = Button(button_reset_ax, "Reset", color="lightcyan", hovercolor="0.95")
button_reset.on_clicked(reset)


# Графік
ax[0].grid(color="0.8", linewidth=1)
ax[1].grid(color="0.8", linewidth=1)
plt.show()