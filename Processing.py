#For Pi 4 Terminal:
"""
For sending input:
#Sleep mode
#echo 0 > /dev/ttyS0

#collect data mode
#echo 1 > /dev/ttyS0

#send data mode
#echo 2 > /dev/ttyS0





For reading output
#cat /dev/ttyS0


"""







arrNoLED = [None] * 40  # Creates a list with 100 `None` elements for data with no LED turned on
arr1550 = [None] * 100  # Creates a list with 100 `None` elements for data with 1550nm LED turned on
arr3400 = [None] * 100  # Creates a list with 100 `None` elements for data with 3400nm LED turned on
tempReadings = [None] * 12  # Creates a list with 100 `None` elements for data with no LED turned on


#Code snippet 10: Assumed Input Data Declerations for Processing.py
arrNoLED = readingData[0:40]         # First 40 elements
arr1550 = readingData[40:140]        # Next 100 elements (40 to 139)
arr3400 = readingData[140:240]       # Next 100 elements (140 to 239)
tempReadings = readingData[240:252]  # Last 12 elements (240 to 251)


#Code snippet 11: Processing Calculations Using a t test in Functions.py
#3400 is A,1
#1550 is B,2

arrD = [None] * 100 # Empty array to hold the difference of each value
for i in arr1550:
    arrD[i] = arr1550[i] - arr3400[i] # Populates array to hold the difference of each value

u1=sum(arr3400)/len(arr3400) # Calculate mean for 3400nm data
u2=sum(arr1550)/len(arr1550) # Calculate mean for 1550nm data

ud=u2-u1 # Calculate difference of means


delta=0.5 # Volts
COI=0.98 # Confidence interval of 98%.
alpha=0.02 # Significance of 2
v=len(arr1550)-1 # Degree of freedom = 100-1 = 99
D=sum(arrD)/len(arrD) # Calculate mean of the differences


# Calculate standard deviation of the difference in data
sumSquared =0
for i in arrD:
    sumSquared=sumSquared+(arrD[i]-D)^2
sD=(sumSquared/(len(arrD)-1))**0.5


tcalc=(D-delta) / (sD/(len(arrD)**0.5)) # Calculate tcalc
tcrit = 2.081 # Fixed tcrit value for significance of 0.02 and degree of freedom of 99. Found using t table.


if tcalc>tcrit:
    #there is water present
    presence_of_water=1
else: presense_of_water=0























import numpy as np

# Example datasets
data_a = np.random.randn(100)  # Replace with your actual data
data_b = np.random.randn(100)  # Replace with your actual data

# Calculate percentage difference in means
mean_a = np.mean(data_a)
mean_b = np.mean(data_b)

percentage_diff = abs(mean_a - mean_b) / mean_a * 100
print(f"Initial Percentage Difference: {percentage_diff:.2f}%")


from scipy.stats import skew, kurtosis

def extract_features(data):
    return {
        "mean": np.mean(data),
        "std_dev": np.std(data),
        "variance": np.var(data),
        "percentile_25": np.percentile(data, 25),
        "percentile_75": np.percentile(data, 75),
        "skewness": skew(data),
        "kurtosis": kurtosis(data)
    }

features_a = extract_features(data_a)
features_b = extract_features(data_b)

print("Features A:", features_a)
print("Features B:", features_b)

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Combine features into a single dataset
features = np.array([[features_a['mean'], features_b['mean'], features_a['std_dev'], features_b['std_dev']]])  # Example features

# Simulated historical data
X = arr1550
y = arr3400

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor()
model.fit(X_train, y_train)

# Predict percentage difference
predicted_difference = model.predict(features)
print(f"Predicted Percentage Difference: {predicted_difference[0]:.2f}%")
