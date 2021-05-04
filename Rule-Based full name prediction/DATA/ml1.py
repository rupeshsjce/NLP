import pandas as pd
from sklearn import datasets, linear_model
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt


# Load the Diabetes dataset
columns = “name1fn name1ln name2_2_fn name2_2_ln name2_1_ln”.split() # Declare the columns names
names = datasets.load_names() # Call the diabetes dataset from sklearn


df = pd.read_csv("data-key-ml.csv", header=columns)
y = names.target # define the target variable (dependent variable) as y

# create training and testing vars
X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=0.2)
print(X_train.shape, y_train.shape)
print(X_test.shape, y_test.shape)

