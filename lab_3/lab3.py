from urllib.request import urlopen
from datetime import datetime
import pandas as pd
import os
import json
from spyre import server
# ^ Завантаження бібліотек ^



# Папка для файлів
if not os.path.exists("csv_folder"):
    os.makedirs("csv_folder")
# Директорія з файлами
files = os.listdir("csv_folder")


def old_code_download():
    files = os.listdir("csv_folder")
    # Отримання/завантаження даних ("i" --> індекс/номер області)
    for i in range(1,28):
        url = "https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={}&year1=1982&year2=2024&type=Mean".format(i)
        text = (urlopen(url)).read()
        # Прибибрання зайвого тексту
        text = text.strip()
        text = text.split(b"\n", 2)[2]
        text = text.replace(b", ", b",")
        text = text.replace(b"<tt><pre>", b"")
        text = text.replace(b"</pre></tt>", b"")
        # Дата та час, що додаються до назви файлу
        load_date = (datetime.today()).strftime("%d-%m-%Y_%H-%M-%S")
        # Видалення старих даних
        for f in files:
            if ("vhi_file_ID"+str(i)+"_") in f:
                ff = os.path.join("csv_folder", f)
                os.remove(ff)
        fname = "vhi_file_ID"+str(i)+"_"+str(load_date)+".csv"
        fpath = os.path.join("csv_folder", fname)
        try:
            out = open(fpath, "wb")
            out.write(text)
            out.close()
            print("Data #{} was downloaded!".format(i))
        except:
            print("Something went wrong with #{}...".format(i))

    print("> Finished <")


def old_code_df():
    # Назви стовпців
    headers = ["Year", "Week", "SMN", "SMT", "VCI", "TCI", "VHI"]
    ind = 0
    dfs = []
    files = os.listdir("csv_folder")
    for f in files:
        ind = ind+1
        ff = os.path.join("csv_folder", f)
        # Читання файлу
        dff = pd.read_csv(ff, index_col=False, header=None, names=headers)
        # Додавання стовпцю з індексами регіонів
        dff["Area"] = ind
        dfs.append(dff)

    # Об'єднання всіх даних в один датафрейм
    df = pd.concat(dfs, axis=0, ignore_index=True)
    # Відкидання відсутніх даних (NaN / -1)
    df = df.drop(df.loc[df["VHI"] == -1].index)
    df = df.reset_index(drop=True)
    ndf = df.copy()
    

    # Зміна індексів
    new_ind = {
        1: 22,
        2: 24,
        3: 23,
        4: 25,
        5: 3,
        6: 4,
        7: 8,
        8: 19,
        9: 20,
        10: 21,
        11: 9,
        12: 26,
        13: 10,
        14: 11,
        15: 12,
        16: 13,
        17: 14,
        18: 15,
        19: 16,
        20: 27,
        21: 17,
        22: 18,
        23: 6,
        24: 1,
        25: 2,
        26: 7,
        27: 5
    }

    def zmina_ind(old_df, nind):
        new_df = old_df.copy()
        new_df["Area"] = new_df["Area"].replace(nind)
        return new_df
        
    df = zmina_ind(ndf, new_ind)
    return df



class LabaApp(server.App):
    title = "NOAA Data Vizualization"
    inputs = [{
            "type": "dropdown",
            "label": "VCI / TCI / CHI",
            "options": [{"label": "VCI", "value": "VCI"},
                        {"label": "TCI", "value": "TCI"},
                        {"label": "VHI", "value": "VHI"}],
            "key": "data_type",
            "action_id": "update_data"},
             {
            "type": "dropdown",
            "label": "Region",
            "options": [
                {"label": "Вінницька", "value": "1"},
                {"label": "Волинська", "value": "2"},
                {"label": "Дніпропетровська", "value": "3"},
                {"label": "Донецька", "value": "4"},
                {"label": "Житомирська", "value": "5"},
                {"label": "Закарпатська", "value": "6"},
                {"label": "Запорізька", "value": "7"},
                {"label": "Івано-Франківська", "value": "8"},
                {"label": "Київська", "value": "9"},
                {"label": "Кіровоградська", "value": "10"},
                {"label": "Луганська", "value": "11"},
                {"label": "Львівська", "value": "12"},
                {"label": "Миколаївська", "value": "13"},
                {"label": "Одеська", "value": "14"},
                {"label": "Полтавська", "value": "15"},
                {"label": "Рівенська", "value": "16"},
                {"label": "Сумська", "value": "17"},
                {"label": "Тернопільська", "value": "18"},
                {"label": "Харківська", "value": "19"},
                {"label": "Херсонська", "value": "20"},
                {"label": "Хмельницька", "value": "21"},
                {"label": "Черкаська", "value": "22"},
                {"label": "Чернівецька", "value": "23"},
                {"label": "Чернігівська", "value": "24"},
                {"label": "Крим", "value": "25"},
                {"label": "м. Київ", "value": "26"},
                {"label": "Севастополь", "value": "27"}],
            "key": "region",
            "action_id": "update_data"
             },
             {
            "type": "text",
            "label": "Week interval",
            "key": "week_interval",
            "value": "1-10",
            "action_id": "update_data"
             },
             {
                 # newlist = [expression for item in iterable]
            "type": "dropdown",
            "label": "Year",
            "options": [{"label": str(x), "value": str(x)} for x in range(1982, 2025)],
            "key": "year",
            "action_id" : "update_data"
             }]
    
    controls = [{"type": "hidden", "id": "update_data"}]
    
    tabs = ["Plot", "Table"]

    outputs = [{
            "type": "plot",
            "id": "plot",
            "control_id": "update_data",
            "tab": "Plot"},
            {
            "type": "table",
            "id": "table_id",
            "control_id": "update_data",
            "tab": "Table",
            "on_page_load": True}]

    def getData(self, params):
        region = params["region"]
        week_interval = params["week_interval"]
        year = params["year"]
        df = old_code_df()
        df = df[df["Area"] == int(region)]
        week_start, week_end = map(int, week_interval.split("-"))
        df = df[(df["Week"] >= week_start) & (df["Week"] <= week_end) & (df["Year"] == int(year))]
        return df[["Year", "Week", "SMN", "SMT", "VCI", "TCI", "VHI"]]

    def getAreaName(self, region):
        region_map = {
            "1": "Вінницька",
            "2": "Волинська",
            "3": "Дніпропетровська",
            "4": "Донецька",
            "5": "Житомирська",
            "6": "Закарпатська",
            "7": "Запорізька",
            "8": "Івано-Франківська",
            "9": "Київська",
            "10": "Кіровоградська",
            "11": "Луганська",
            "12": "Львівська",
            "13": "Миколаївська",
            "14": "Одеська",
            "15": "Полтавська",
            "16": "Рівенська",
            "17": "Сумська",
            "18": "Тернопільська",
            "19": "Харківська",
            "20": "Херсонська",
            "21": "Хмельницька",
            "22": "Черкаська",
            "23": "Чернівецька",
            "24": "Чернігівська",
            "25": "Крим",
            "26": "м. Київ",
            "27": "Севастополь"
        }
        return region_map.get(region, "")
    
    def getPlot(self, params):
        df = self.getData(params)
        data_type = params["data_type"]
        year = params["year"]
        region = params["region"]
        week_interval = params["week_interval"]
        y_label = data_type
        x_label = "Weeks"
        region_name = self.getAreaName(region)
        week_start, week_end = map(int, week_interval.split("-"))
        plt_obj = df.plot(x="Week", y=data_type, legend=False)
        plt_obj.set_ylabel(y_label)
        plt_obj.set_xlabel(x_label)
        plt_obj.set_title(f"{data_type} for {region_name}, {int(year)} year, {week_start}-{week_end} weeks")
        fig = plt_obj.get_figure()
        return fig
        


if __name__ == "__main__":
    old_code_download()
    app = LabaApp()
    app.launch()