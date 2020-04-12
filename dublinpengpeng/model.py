#!/usr/bin/env python
# coding: utf-8

# ## COMP30830 - Software Engineering
# ### Project: DublinBikes  
# Group work by:  
# 
# **Xi Jiang  
# Yuqian Shu  
# Yi Zhang**

# ### Machine Learning prediction model
# In this notebook we develop a ML model to predict two key values that are functional to our web application:  
#   
# **number of available bikes for a selected station  
# number of available bike stands for a selected station**  
#   
# The model is trained on data fetched from an Amazon RDS database, where we store historical data referring to:
#   
# real-time information that Dublin Bikes makes available through their web API  
# Dublin weather information from OpenWeather, obtained by a web API  
# ***N.B.:*** all database data are kept up-to-date.

# ### Getting started
# First of all, we need to import Python packages that are required to our model, as well as fetching the data from the Amazon RDS database.

# #### Import required packages
# A number of Python packages are required for our model in order to work, so we import them in our Notebook.

# In[ ]:


import pickle 
#import seaborn as sns
#import matplotlib.pyplot as plt
import pandas as pd 
#import numpy as np 
#import json
import pymysql

#from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
#from sklearn.preprocessing import PolynomialFeatures
#from sklearn.pipeline import make_pipeline
#from patsy import dmatrices
from sklearn import metrics
#from sklearn.model_selection import cross_validate


# #### Connect to Amazon RDS database
# After having stored all the necessary credentials in specific variables, we connect to the database providing error-handling in case of connection issues.

# In[ ]:


# Attempt connection to database
# Print a statement on the screen to check whether the connection is working
try:
    con = pymysql.connect(host='dublinbike.cczltqdfsp1t.eu-west-1.rds.amazonaws.com', user='root', passwd='shuyuqian',db='dublin')
    print('+=========================+')
    print('|    TRYING TO CONNECT    |')
    print('+=========================+')
    print('|        SUCCESS!         |')
    print('+=========================+')
    
# Exit if connection not working   
except Exception as e:
        sys.exit(e)


# #### Data fetching
# Bikes information
# We store real-time data from Dublin Bikes in a relation named "availability" in the RDS database schema.  
# We store weather data from OpenWeather in a relation named "weather" in the RDS database schema.
#   
# We fetch Pandas dataframe object and we examine it.
# 
# ***N.B.:***We started scrapping the bikes data on 02/03/2020

# In[ ]:


# Create dataframe and store data running SQL query
df_AllStations = pd.read_sql_query("select *,cast(str_to_date(availability.datetime,'%d-%b-%Y (%H:%i:%s.%f)' )as datetime) as datetimeB FROM dublin.availability, dublin.Weather having abs(datetimeB-Weather.dateTime)<30000 and Weather.dateTime<'2020/3/29'", con)

# Examine dataframe object, show first 10 rows
df_AllStations.head(5)


# In[ ]:


df_AllStations.shape


# In[ ]:


#create column for day of the week
df_AllStations['weekday'] = df_AllStations['datetimeB'].dt.dayofweek
df_AllStations['hour'] = df_AllStations['datetimeB'].dt.hour
df_AllStations['minutes'] = df_AllStations['datetimeB'].dt.minute


# In[ ]:


#use number to replace weekdays
df_AllStations['weekday'] = df_AllStations['weekday'].replace(0, 'Monday')
df_AllStations['weekday'] = df_AllStations['weekday'].replace(1, 'Tuesday')
df_AllStations['weekday'] = df_AllStations['weekday'].replace(2, 'Wednesday')
df_AllStations['weekday'] = df_AllStations['weekday'].replace(3, 'Thursday')
df_AllStations['weekday'] = df_AllStations['weekday'].replace(4, 'Friday')
df_AllStations['weekday'] = df_AllStations['weekday'].replace(5, 'Saturday')
df_AllStations['weekday'] = df_AllStations['weekday'].replace(6, 'Sunday')


# In[ ]:


#show all the columns of the dataframe
df_AllStations.columns


# ### Dummy coding(categorical -> continuous)

# We need to incorporate the following information (variables) in our model, but they are not immediately usable as they come in a categorical form:  
# **cloud coverage  
# day of the week**  
# Thus, we transform them in a series of dummy variables. The process is known as "dummy coding".

# In[ ]:


# Create a separate dataframe with days of the week (categorical)
data_input1 = pd.DataFrame(df_AllStations['weekday'])

# Create a separate dataframe with cloud coverage information (categorical)
data_input2 = pd.DataFrame(df_AllStations['weatherMain'])

# Concatenate the two dataframes in the main one
dummy = pd.get_dummies(data_input1)
dummy_2 = pd.get_dummies(data_input2)
df_AllStations = pd.concat([df_AllStations,dummy],axis=1)
df_AllStations = pd.concat([df_AllStations,dummy_2],axis=1)


# In[ ]:


## Examine dataframe object, show first rows
df_AllStations.head()


# ### Check dataframe state

# #### New columns
# The new dummy coded variables have been concatenated at the end of the dataframe, so we now check our dataframe shape.

# In[ ]:


# Show number of rows and columns of the dataframe
print("The dataset has %s rows and %s columns." % df_AllStations.shape)


# #### Data types
# As a further check, we analyze the data type in our dataframe.

# In[ ]:


df_AllStations.dtypes


# ### ML model
# In order to predict our two target variables  
# 
# **number of available bikes  
# number of available bike stands**  
# we need two differnt ML models that are trained in the following section.  
# After having tested the regression model as a viable alternative, we decided to implement a *Random Forest* classifier model, as it proves to be a more effective predictor.
#   
#  ***N.B.:*** we train our models on a random selection of 2/3 of the original dataset. We perform testing on the remain

# #### (1)Predict the number of available bikes

# **model training**

# In[ ]:


# Select model features and store them in a new dataframe
input_model = pd.DataFrame(df_AllStations[['number','temperature','windSpeed','hour','weekday_Friday', 'weekday_Monday',
       'weekday_Saturday', 'weekday_Sunday', 'weekday_Thursday',
       'weekday_Tuesday', 'weekday_Wednesday']])
input_model = pd.concat([input_model,dummy_2],axis=1)

# Define target variable
output = df_AllStations['available_bikes']


# In[ ]:


# Split dataset to train and test
X_train,X_test,Y_train,Y_test=train_test_split(input_model,output,test_size=0.33,random_state=42)
print("Training the model on %s rows and %s columns." % X_train.shape)


# In[ ]:


# Instantiate RandomForestRegressor object calling 10 decision tree models
rf = RandomForestRegressor(n_estimators=10)

# Train the model
rf.fit(X_train, Y_train)

print("Testing the model on %s rows." % Y_test.shape[0])


# **model testing**  
# Using the trained model to predict the target feature availablebikes on the testing dataset

# In[ ]:


# Get prediction for test cases
prediction = rf.predict(X_test)

#make a new datafram to show the predicted available bikes
DF_Predicated = pd.DataFrame(prediction, columns=['Predicted'])

#convert all the data for testing to a new datafram
DF_Alltest = df_AllStations.iloc[Y_test]

#reset the index
DF_Bikes = pd.DataFrame(DF_Alltest['available_bikes']).reset_index(drop=True)

#to get a clear comparisaon, concatenate two new datafram
actual_vs_predicted= pd.concat([DF_Bikes,DF_Predicated], axis=1)


# In[ ]:


print("\nPredictions with multiple linear regression: \n")
actual_vs_predicted


# **Model evaluation**  
# In order to evaluate the prediction effectiveness of our model, we compute the mean-absolute error, the mean squared error,the root-mean-square deviation and R2.

# In[ ]:


def printMetrics(testActualVal, predictions):
    #classification evaluation measures
    print('Error Evaluation')
    print('==============================================================================')
    print("MAE (Mean Absolute Error): ", metrics.mean_absolute_error(testActualVal, predictions))
    print("MSE (Mean Squared Error): ", metrics.mean_squared_error(testActualVal, predictions))
    print("RMSE (Root Mean Squared Error): ", metrics.mean_squared_error(testActualVal, predictions)**0.5)
    print("R2: ", metrics.r2_score(testActualVal, predictions))


# In[ ]:


printMetrics(Y_test, prediction)


# The R² value implies that there is 94% less variation around the line than the mean. In other words, the relationship between the input variables and the number of available bikes accounts for 94% of the variation.

# **Module integration**  
# In order to connect the ML model to our Flask web application, we need to produce a 'prediction-data' file from the trained model using the ***Pickle*** Python module.  
# Pickle allows us to store the prediction model in a file that we save on the server, in order to be used by the application to actually deliver a prediction based on the requested stations by the user.

# In[ ]:


pickle.dump(rf,open('final_prediction_bike.pickle', 'wb'))


# This is not strictly functional to the application
random_forest = pickle.load(open("final_prediction_bike.pickle", "rb"))


# #### (2)Predict the number of available bikes

# **model training**

# In[ ]:


# Select model features and store them in a new dataframe
input_model = pd.DataFrame(df_AllStations[['number','temperature','windSpeed','hour','weekday_Friday', 'weekday_Monday',
       'weekday_Saturday', 'weekday_Sunday', 'weekday_Thursday',
       'weekday_Tuesday', 'weekday_Wednesday']])
input_model = pd.concat([input_model,dummy_2],axis=1)

# Define target variable
output = df_AllStations['available_bike_stands']


# In[ ]:


# Split dataset to train and test
X_train,X_test,Y_train,Y_test=train_test_split(input_model,output,test_size=0.33,random_state=42)
print("Training the model on %s rows and %s columns." % X_train.shape)

# Instantiate RandomForestRegressor object calling 10 decision tree models
rf2 = RandomForestRegressor(n_estimators=10)

# Train the model
rf2.fit(X_train, Y_train)

print("Testing the model on %s rows." % Y_test.shape[0])


# **model testing**
#   
#  Using the trained model to predict the target feature availablebikes on the testing dataset

# In[ ]:


# Get prediction for test cases
prediction = rf2.predict(X_test)

#make a new datafram to show the predicted available bikes
DF_Predicated = pd.DataFrame(prediction, columns=['Predicted'])

#convert all the data for testing to a new datafram
DF_Alltest = df_AllStations.iloc[Y_test]

#reset the index
DF_Stands = pd.DataFrame(DF_Alltest['available_bike_stands']).reset_index(drop=True)

#to get a clear comparisaon, concatenate two new datafram
actual_vs_predicted= pd.concat([DF_Stands,DF_Predicated], axis=1)


# In[ ]:


print("\nPredictions with multiple linear regression: \n")
actual_vs_predicted


# **model evaluation**  
# In order to evaluate the prediction effectiveness of our model, we compute the mean-absolute error, the mean squared error,the root-mean-square deviation and R2.

# In[ ]:


def printMetrics(testActualVal, predictions):
    #classification evaluation measures
    print('Error Evaluation of stands')
    print('==============================================================================')
    print("MAE (Mean Absolute Error): ", metrics.mean_absolute_error(testActualVal, predictions))
    print("MSE (Mean Squared Error): ", metrics.mean_squared_error(testActualVal, predictions))
    print("RMSE (Root Mean Squared Error): ", metrics.mean_squared_error(testActualVal, predictions)**0.5)
    print("R2: ", metrics.r2_score(testActualVal, predictions))


# In[ ]:


printMetrics(Y_test, prediction)


# The R² value implies that there is 94% less variation around the line than the mean. In other words, the relationship between the input variables and the number of available bikes accounts for 94% of the variation.

# **Module integration**  
# In order to connect the ML model to our Flask web application, we need to produce a 'prediction-data' file from the trained model using the ***Pickle*** Python module.  
# Pickle allows us to store the prediction model in a file that we save on the server, in order to be used by the application to actually deliver a prediction based on the requested stations by the user.

# In[ ]:


pickle.dump(rf2,open('final_prediction_bike_stands.pickle', 'wb'))

# This is not strictly functional to the application
random_forest_stands=pickle.load(open("final_prediction_bike_stands.pickle", "rb"))

