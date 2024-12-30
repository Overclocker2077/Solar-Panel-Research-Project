import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import os
from rich import print as pr

np.set_printoptions(precision=3, suppress=True)
sns.set_theme()

from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


# print(tf.__version__)

# pre: 2d array of strings 
# post: returns a string array with the column names and a dictionary with the colomn name pair with the data in that column
def convertDataFrame(dataframe) -> dict[str, list[float]]:
    array = dataframe.to_numpy().tolist()
    column_names = array.pop(0)
    table = {}
    for name in column_names:
        table[name] = list()
    # print(table)
    for r in range(len(array)):
        for c in range(len(array[r])):
            table[column_names[c]].append(float(array[r][c]))
    return table

# pre: 2d array, and target_index is the values to be filter by the key_index, using the split_value
# post: returns two lists containing the divided data set based on the key_index and split_func
def split_filter(dict, target_index, key_index, split_func = lambda x : x > 65 and x < 80) -> tuple[list[float], list[float]]:
    array1 : list[float] = [] # room 
    array2 : list[float] = [] # below
    array3 : list[float] = [] # above
    for i in range(len(dict[target_index])):
        if (split_func(dict[key_index][i])):
            array1.append(dict[target_index][i])
        elif (dict[key_index][i] < 65):
            array2.append(dict[target_index][i])
        else:
            array3.append(dict[target_index][i])
    return array1, array2, array3

def Polynomial_regression(degree: int = 1) -> tuple[np.poly1d, np.poly1d, np.ndarray, np.ndarray, np.poly1d, np.ndarray]:
    fc_room, fc_below, fc_above = split_filter(dict = data_table, target_index=columns[2], key_index=columns[3])
    dcv_room, dcv_below, dcv_above = split_filter(dict = data_table, target_index=columns[4], key_index=columns[3])
    
    model_room_temp = np.poly1d(np.polyfit(x = fc_room,  y = dcv_room, deg = degree))
    polyline_room_temp = np.linspace(1, 4000, 50)

    model_above_temp = np.poly1d(np.polyfit(x = fc_above,  y = dcv_above, deg = degree))
    polyline_above_temp = np.linspace(1, 4000, 50)

    model_below_temp = np.poly1d(np.polyfit(x = fc_below,  y = dcv_below, deg = degree))
    polyline_below_temp = np.linspace(1, 4000, 50)

    return model_below_temp, model_room_temp, polyline_below_temp, polyline_room_temp, model_above_temp, polyline_above_temp

def plot_data():
    model_below_temp, model_room_temp, polyline_below_temp, polyline_room_temp, model_above_temp, polyline_above_temp = Polynomial_regression(4)
    
    #model_below_temp, model_room_temp, polyline_below_temp, polyline_room_temp = Logarithmic_regression()

    plt.scatter(x = data_table[columns[2]], y = data_table[columns[4]], label='Data', c = data_table[columns[3]], cmap="turbo")
    plt.plot(polyline_room_temp, model_room_temp(polyline_room_temp), color = "Orange")
    plt.plot(polyline_below_temp, model_below_temp(polyline_below_temp), color = "Blue")
    plt.plot(polyline_above_temp, model_above_temp(polyline_above_temp), color = "Red")
    print(model_below_temp)
    print(model_room_temp)
    print(model_above_temp)
    color_bar = plt.colorbar()
    color_bar.set_label("Temperature (F)")
    plt.xlabel('Light Intensity (Fc)')
    plt.ylabel('Energy Output (DCV)')
    plt.legend()
    plt.grid(True)

# plot_data()

# plt.title('Solar Panel Data') 
# plt.show()


class Polynomial_Prediction_Model():

    def __init__(self, df, predict_column, degree):
        self.df = df
        self.degree = degree
        self.columns = df.columns.tolist()
        self.columns.pop(4)
        self.predict_column = predict_column

        self.input_features = df[self.columns].values
        self.output_feature = df[self.predict_column].values
        self.model = None
        self.x_poly = None

        # self.train_dataset = df.sample(frac=0.8, random_state=0)
        # self.test_dataset = df.drop(self.train_dataset.index)
        # self.train_features = self.train_dataset.copy()
        # self.test_features = self.test_dataset.copy()
        # self.train_labels = self.train_features.pop(self.predict_column)
        # self.test_labels = self.test_features.pop(self.predict_column)
        # self.model = None

    # Pre: Normaization axis automatically set to -1, epochs set to 100 
    # Post: train and returns training history 
    def compile(self, axis = -1):
        if (self.model == None):
            self.poly = PolynomialFeatures(degree = self.degree, include_bias = False)
            self.x_poly = self.poly.fit_transform(self.input_features)

            X_train, X_test, y_train, y_test = train_test_split(self.x_poly, self.output_feature, test_size=0.2, random_state=42)

            self.model = LinearRegression()
            self.model.fit(self.x_poly, self.output_feature)
        else:
            raise AttributeError("Model has already been compiled.")
    
    def predict(self, features: np.ndarray):
        if (self.model != None):
            poly = PolynomialFeatures(degree = self.degree, include_bias = False)
            x_poly = poly.fit_transform(features)

            return self.model.predict(x_poly)
        raise AttributeError("Must compile the model before calling predict.")

    def save(self, model_name):
        ...

    def load(self, path):
        ...

    def summary(self):
        ...

    def plot(self, x,y, name = "Data"):
        plt.scatter(self.df["Fc"], self.df[self.predict_column], label = name)
        plt.scatter(x, y, color="Orange", label = "Predictions")
        plt.ylim(0,6)
        plt.colorbar()
        plt.ylabel("Energy Output (DCV)")
        plt.xlabel("Light Intensity (Fc)")
        plt.legend()
    
    def plot_loss(self, loss: np.ndarray[float]):
        x = [i for i in range(len(loss))]
        plt.scatter(x, loss, label='val_loss points')
        plt.plot(loss, label='val_loss')
        plt.ylim([0, 10])
        plt.xlabel('Tests Data')
        plt.ylabel(f'Error |prediction - actual|')
        plt.legend()
        plt.grid(True)
        
    def calc_loss(self, output_prediction) -> tuple[np.ndarray[float], float]:
        output_prediction = output_prediction.tolist()
        loss = []
        total = 0    
        for i in range(len(output_prediction)):
            loss.append(abs(float(df["DCV Output"].iloc[i]) - float(output_prediction[i])))
            total += loss[i]
        avg_loss = total / len(loss)

        return np.array(loss), avg_loss


if (__name__ == "__main__"):
    columns = ["Vertical Angle", "Horizontal Angle", "Fc", "TempF", "DCV Output"]
    raw_dataset = pd.read_csv("Solar Panel Data - Sheet1.csv", names=columns)

    # sorted_dataset = raw_dataset.sort_values(by=[columns[4]], ascending=True)
    # pr(dataset)
    data_table = convertDataFrame(raw_dataset)
    df_raw = pd.DataFrame.from_dict(data_table)
    df = df_raw.copy()
    #print(df)

    model = Polynomial_Prediction_Model(df, columns[4], 4)
    model.compile()
    y_prediction = model.predict(model.input_features)
    #print(y_prediction)
    # print(y_prediction.shape)
    # print(model.input_features.shape)
    # model.plot(x = model.df["Fc"], y = y_prediction)

    loss, avg_loss = model.calc_loss(y_prediction)
    print(loss)
    print(f"Avg loss: {avg_loss}")
    
    model.plot_loss(loss)

    plt.show()

# 4th degree Avg loss: 0.11494852884846171
# 5th degree Avg loss: 0.058064411397904046
# 6th degree Avg loss: 0.46999121531433935
