import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, CheckButtons
# ^ Завантаження бібліотек ^


# y = kx + b
def generate_data(num_points, k, b, noise_level):
    x = np.linspace(0, 10, num_points)
    noise = np.random.normal(0, noise_level, num_points)
    y = k*x + b + noise
    return x, y

# Метод найменших квадратів (МНК)
def mnk(x, y):
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    xy_mean = np.mean(x*y)
    x_sq_mean = np.mean(x**2)
    k = (xy_mean - x_mean*y_mean) / (x_sq_mean - x_mean**2)
    b = y_mean - k*x_mean
    return k, b

# Згенеровані дані
true_k = 2
true_b = 5
num_points = 100
noise_level = 2
x, y = generate_data(num_points, true_k, true_b, noise_level)

# Оцінки параметрів k та b (наша функція ↑ та np.polyfit)
mnk_k, mnk_b = mnk(x, y)
polyfit_k, polyfit_b = np.polyfit(x, y, 1)

# Результати
text_results = f"""Метод найменших квадратів (МНК):
    k: {mnk_k}
    b: {mnk_b}

np.polyfit:
    k: {polyfit_k}
    b: {polyfit_b}

Початкова пряма:
    k: {true_k}
    b: {true_b}"""

fig, ax = plt.subplots(figsize=(12, 8))
fig.subplots_adjust(top=0.7, left=0.1, bottom=0.08)


# TextBox для результутів
ax_text = plt.axes([0.1, 0.71, 0.6, 0.25])
text_box = TextBox(ax_text, "Results:", initial=text_results)

# Checkbox для ліній
ax_MNK = plt.axes([0.71, 0.71, 0.19, 0.25])
check_lines = CheckButtons(ax_MNK, ["МНК", "np.polyfit"], [True, True])

# Update (оновлення параметрів)
def update(val):
    MNK_status = check_lines.get_status()[0]
    polyfit_status = check_lines.get_status()[1]
    if MNK_status:
        lineMNK.set_visible(True)
    else:
        lineMNK.set_visible(False)
    if polyfit_status:
        linepoly.set_visible(True)
    else:
        linepoly.set_visible(False)
    fig.canvas.draw_idle()

check_lines.on_clicked(update)


# Графік
ax.scatter(x, y, color="black", label="Дані")
line, = ax.plot(x, true_k*x + true_b, color="red", label="Пряма")
lineMNK, = ax.plot(x, mnk_k*x + mnk_b, color="green", label="МНК")
linepoly, = ax.plot(x, polyfit_k*x + polyfit_b, color="blue", label="np.polyfit")
ax.legend()
ax.grid(color="0.8")
plt.show()