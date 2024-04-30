import numpy as np
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, Button, CheckboxGroup, Dropdown
from bokeh.plotting import figure
from bokeh.server.server import Server
# ^ Завантаження бібліотек ^


t = np.linspace(0, 10, 1000)

# Дефолтні параметри
default_amplitude = 1
default_frequency = 1
default_phase = 0
default_noise_mean = 0
default_noise_covariance = 0.05
default_show_noise = False
default_color = "red"
default_window_size = 10

last_noise_mean = default_noise_mean
last_noise_covariance = default_noise_covariance

# Шум
noise = np.random.multivariate_normal([default_noise_mean], [[default_noise_covariance]], len(t))[:,0]


def all_code(doc):
    # Функція
    def generate_noise(mean, covariance, length):
        global noise
        noise = np.random.multivariate_normal([mean], [[covariance]], length)[:,0]

    def harmonic_with_noise(t, amplitude, frequency, s_phase, noise_mean, noise_covariance, show_noise):
        graph = amplitude * np.sin(2 * np.pi * frequency * t + s_phase)
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
        
    # Відфільтрований шум (свій)  >>>  Moving average (Ковзне/рухоме середнє)
    def harmonic_with_noise_filtered(noised_graph, w):
        filtered_graph = np.zeros_like(noised_graph)
        window_size = w
        for i in range(len(noised_graph)):
            start_index = max(0, i - window_size // 2)
            end_index = min(len(noised_graph), i + window_size // 2 + 1)
            filtered_graph[i] = np.mean(noised_graph[start_index:end_index])
        return filtered_graph

    g_default = harmonic_with_noise(t, default_amplitude, default_frequency, default_phase, default_noise_mean, default_noise_covariance, default_show_noise)
    source = ColumnDataSource(data=dict(x=t, y=g_default))
    source2 = ColumnDataSource(data=dict(x=t, y=harmonic_with_noise_filtered(g_default, default_window_size)))

    # Графік
    p = figure(width=800, height=400, y_range=(-1, 1), x_range=(0, 10))
    line = p.line(source=source, color=default_color, line_width=2)
    p2 = figure(width=800, height=400, y_range=(-1, 1), x_range=(0, 10))
    line2 = p2.line(source=source2, color="magenta", line_width=2)


    # Слайдери
    s_amplitude = Slider(start=0.1, end=2.0, value=default_amplitude, step=0.1, title="Amplitude")
    s_frequency = Slider(start=0.1, end=5.0, value=default_frequency, step=0.1, title="Frequency")
    s_phase = Slider(start=0, end=2*np.pi, value=default_phase, step=0.1, title="Phase")
    s_noise_mean = Slider(start=-1, end=1, value=default_noise_mean, step=0.1, title="Noise Mean")
    s_noise_covariance = Slider(start=0.01, end=1, value=default_noise_covariance, step=0.01, title="Noise Covariance")
    s_window_size = Slider(start=5, end=50, value=10, step=1, title="Window Size (for filter)")

    # Чекбокс
    checkbox_show_noise = CheckboxGroup(labels=["Show noise"])

    # Dropdown
    menu = [("Red", "red"), ("Green", "green"), ("Blue", "blue")]
    dropdown_button = Dropdown(label="Colors", button_type="default", menu=menu)


    # Update (оновлення параметрів)
    def update(attrname, old, new):
        amplitude = s_amplitude.value
        frequency = s_frequency.value
        phase = s_phase.value
        noise_mean = s_noise_mean.value
        noise_covariance = s_noise_covariance.value
        w = s_window_size.value
        if 0 in checkbox_show_noise.active:
            show_noise = True
        else:
            show_noise = False
        g = harmonic_with_noise(t, amplitude, frequency, phase, noise_mean, noise_covariance, show_noise)
        source.data = dict(x=t, y=g)
        source2.data = dict(x=t, y=harmonic_with_noise_filtered(g, w))

    def color_update(event):
        new_color = event.item
        line.glyph.line_color = new_color

    s_amplitude.on_change("value", update)
    s_frequency.on_change("value", update)
    s_phase.on_change("value", update)
    s_noise_mean.on_change("value", update)
    s_noise_covariance.on_change("value", update)
    s_window_size.on_change("value", update)
    checkbox_show_noise.on_change("active", update)
    dropdown_button.on_click(color_update)


    # Reset (скидання параметрів)
    def reset(event):
        s_amplitude.value = default_amplitude
        s_frequency.value = default_frequency
        s_phase.value = default_phase
        s_noise_mean.value = default_noise_mean
        s_noise_covariance.value = default_noise_covariance
        s_window_size.value = default_window_size
        checkbox_show_noise.active = []
        line.glyph.line_color = default_color
        g_default = harmonic_with_noise(t, default_amplitude, default_frequency, default_phase, default_noise_mean, default_noise_covariance, default_show_noise)
        source.data = dict(x=t, y=g_default)
        source2.data = dict(x=t, y=harmonic_with_noise_filtered(g_default, default_window_size))

    button_reset = Button(label="Reset", button_type="warning")
    button_reset.on_event("button_click", reset)


    doc.add_root(row(column(p, p2), column(button_reset, checkbox_show_noise, dropdown_button, s_amplitude, s_frequency, s_phase, s_noise_mean, s_noise_covariance, s_window_size)))


server = Server({"/": all_code})
server.start()

if __name__ == "__main__":
    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()