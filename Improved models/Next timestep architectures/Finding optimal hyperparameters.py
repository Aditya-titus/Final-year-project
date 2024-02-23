# Finding optimal hyperparameters 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import tensorflow as tf
from itertools import product


# Read data and define input and output
data = pd.read_excel('C:/Users/ADITYA/OneDrive - Imperial College London/Year 4/FYP/Final-year-project/Data formatting/Dataset_scaled_denoised.xlsx')
data = data[data['I'] == 1.6]
X = data.iloc[:,:9]
X = X.drop('S4_cur', axis = 1)
X = X.drop('S1_cur', axis = 1)
X = X.drop('I', axis = 1)
X = X.drop('Sp_cur', axis = 1)

y = X.iloc[2:,:]
X = X.iloc[1:-1,:]



# Set random seeds for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

# Set deterministic GPU usage
tf.config.experimental.set_visible_devices([], 'GPU')



# Define test and train datasets
X_numpy = X.values
y_numpy = y.values

# Split the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X_numpy, y_numpy, test_size=0.2, random_state=42)


# Function to iterate through different criterias
def create_model(hidden_layers=1, activation='relu', batch_size=32):
    model = Sequential()
    model.add(Dense(10, activation=activation, input_dim=X_train.shape[1]))
    for _ in range(hidden_layers):
        model.add(Dense(10, activation=activation))
    model.add(Dense(1, activation='linear'))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# Define the hyperparameters to search over
epochs_range = [10]
hidden_layers_range = [1, 2, 3]
activation_functions = ['relu']
batch_sizes = [16, 32]


# Initialize lists to store results
results = []
best_mse = float('inf')
best_params = {}



# Perform grid search over hyperparameters
for epochs, hidden_layers, activation, batch_size in product(epochs_range, hidden_layers_range, activation_functions, batch_sizes):
    # Create and train the model
    model = create_model(hidden_layers=hidden_layers, activation=activation)
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0, validation_data=(X_test, y_test))
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    
    # Store results
    results.append((epochs, hidden_layers, activation, batch_size, mse))
    
    # Update best parameters if MSE is lower
    if mse < best_mse:
        best_mse = mse
        best_params = {'epochs': epochs, 'hidden_layers': hidden_layers, 'activation': activation, 'batch_size': batch_size}

# Print the most optimal solution
print("Most optimal solution:")
print("Hyperparameters:", best_params)
print("Mean Squared Error:", best_mse)

# Plot MSE for each combination of hyperparameters over epochs
for epochs, hidden_layers, activation, batch_size, mse in results:
    plt.plot(history.history['loss'], label=f'Epochs: {epochs}, Hidden Layers: {hidden_layers}, Activation: {activation}, Batch Size: {batch_size}')
plt.xlabel('Epochs')
plt.ylabel('Mean Squared Error')
plt.legend()
plt.title('Mean Squared Error over Epochs for Different Hyperparameters')
plt.show()