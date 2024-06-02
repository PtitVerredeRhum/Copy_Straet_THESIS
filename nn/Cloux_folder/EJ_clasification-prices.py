#!/usr/bin/env python
# coding: utf-8

# <img src="data/imagen2.png" alt="Drawing" style="width: 1100px;"/>

# # EXERCISE
# # Supervised Learning: Classification.
# 
# ## *Binary electricity price classification in the Day-Ahead Spot Market*

# **Objective:** Imagining that we are in the middle of 2020, predict in which hours the price of electricity in the Day-Ahead Market will be high, being **class 0** for values lower than 40 €, and **class 1** for values higher than 40 €.  We will use the context and historical data for **2020** of the target variable we want to classify and other features that can help to predict the model.
# 
# ### Before you start:
# 
# * In the file **EJ2-data-prices.xlsx** is the input dataset for this example (attributes + label). 
# * Data from January 2, 2020 to June 26, 2020.
# 

# ## **Import libraries and data**
# 

# In[9]:


import sklearn
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the input dataset
### your code here
df = pd.read_excel('EJ2-data-precios.xlsx')


# ## **2. Understanding the data**
# 
# It is necessary to visualize and understand the data we are going to work with, as well as to know its characteristics. 
# 
# 1. How much data is there? How many attributes are there in the data?  
# 2. What do they mean?
# 3. Is there any missing data? 
# 4. Are the labels balanced? 
# 5. Statistical summary of the input data set.

# 1. **How much data is there? How many attributes are there in the data?**

# In[10]:


# Data rows/columns
### your code here
df.columns




# In[27]:


# Calculation of correlation coefficients

### your code here
corr_matrix = df.corr(method='spearman')
# Remove repeated values
mask = np.zeros_like(corr_matrix, dtype=bool)
mask[np.triu_indices_from(mask)] = True

  
f, ax = plt.subplots(figsize=(12, 12))
#Generate Heat Map,
sns.heatmap(corr_matrix, annot=True, fmt=".2f" , mask=mask,)
    # xticks
plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns);
    # yticks
plt.yticks(range(len(corr_matrix.columns)), corr_matrix.columns)
    # plot
plt.show()


# ## *4. Prepare the data*.
# 
# 1. Missing data
# 2. Data cleaning (remove outliers).
# 3. LabelEncoding (we have already done it).
# 4. Feature engineering
# 5. Transformation.

# First, I divide the data into **attributes**: X (features) and **tags**: y (target).

# In[28]:


# Atributes X (features); labels y (target)
### your code here
X = df.drop(columns=['precio'])  # Dropping the 'precio' column to keep the rest as attributes
y = df['precio']  # Selecting only the 'precio' column as the target

print(f"Attributes (X) Shape: {X.shape}")
print(f"Target (y) Shape: {y.shape}")


# **Missing data**
# 
# Check whether Nan exists in the input data.
# 
# - The following method is used [fillna] from Pandas.
# 
# - Learn more about how to allocate values with [Scikit Learn]
# 
# [Scikit Learn]: https://scikit-learn.org/stable/modules/impute.html
# [fillna]: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.fillna.html
# 
# 
# 
# 

# In[29]:


# Check for missing data in attributes
### your code here
nan_values = X.isnull().values.any()
if nan_values:
    print("There are NaN values in the input data.")
else:
    print("There are no NaN values in the input data.")


# In[30]:


# Fill the missing values of each attribute with the previous value of the attribute. 
### your code here
X.fillna(method='ffill', inplace=True)


# In[31]:


# Check for missing data in the target
### your code here
nan_values_y = y.isnull().values.any()
if nan_values_y:
    print("There are NaN values in the input data.")
else:
    print("There are no NaN values in the input data.")


# In[32]:


# Check that no value is missing

### your code here
missing_values = X.isnull().any().any()

if not missing_values:
    print("No missing values present after forward-fill.")
else:
    print("There are still missing values in the DataFrame.")


# In[33]:


# Check that no value is missing

### your code here
missing_values_y = y.isnull().any().any()

if not missing_values_y:
    print("No missing values present after forward-fill.")
else:
    print("There are still missing values in the DataFrame.")


# **3. Feature engineering**
# 
# Using the correlation matrix, eliminate the attributes with a correlation close to 0 with the **"price"** tag. 
# 
# **Which attribute(s) are eliminated?**

# In[34]:


# Delete the attribute
### your code here
correlation_matrix = df.corr()

# Get correlations with 'price' tag
price_correlations = correlation_matrix['precio']
print(price_correlations)


# In[35]:


threshold = 0.1  

# Select attributes with a correlation close to zero with 'price'
attributes_to_drop = price_correlations[abs(price_correlations) < threshold].index.tolist()
print(attributes_to_drop)


# In[36]:


X


# In[37]:


# Drop the selected attributes from the DataFrame
X = X.drop(attributes_to_drop, axis=1)


# In[ ]:





# In[ ]:





# In[ ]:





# In[38]:


X


# ## *5. Split data*
#  

# In[39]:


from sklearn.model_selection import train_test_split

test_size = 0.2  # percentage of the input data that you will use to validate the model

### your code here

# Diviser les données en ensembles d'entraînement et de test (80% pour l'entraînement et 20% pour les tests)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
X_train


# **4. Transformation (scaling, if neccesary)**. 
# 
# * **Scale the data using the *MinMaxScaler()* method within the range [0,1].**

# In[40]:


from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
df_scaled = X.copy()
X_scaled = pd.DataFrame(scaler.fit_transform(df_scaled))
X_scaled.head()


# In[41]:


X_scaled.columns = df_scaled.columns
#df_scaled.columns
X_scaled.head()


# ## *6.  Model building and evaluation*

# * Select **[balanced_accuracy]** as evaluation metric. 
# * Evaluation metrics available in [Scikit-Learn].
# 
# 
# [Scikit-Learn]: https://scikit-learn.org/stable/modules/model_evaluation.html
# 
# [balanced_accuracy]: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.balanced_accuracy_score.html
# 
# * Remember to always use the same random_state to be able to compare results. 

# In[42]:


get_ipython().system('pip install xgboost')


# In[43]:


from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
import xgboost as xgb

num_folds = 15
error_metrics = {'balanced_accuracy'}
models = { ('LR', LogisticRegression(solver='saga')), 
        ### your code here   
          ('RF', RandomForestClassifier()),
          ('KNN', KNeighborsClassifier()),
          ('MLP', MLPClassifier()),
          ('XGB', xgb.XGBClassifier())
        }
results = [] # stores the results of the evaluation metrics
names = [] # name of each algorithm
msg = [] # print the summary of the cross-validation method


# * Which one obtains better results? 
# * Which balanced_accuracy do you get? 

# In[44]:


from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.model_selection import StratifiedKFold

# Cross-validation training
for scoring in error_metrics:
    print('Evaluation metrics: ', scoring)
    for name, model in models:
        print('Model ', name)
        cross_validation = StratifiedKFold(n_splits=num_folds, random_state=0, shuffle=True)
        cv_results = cross_val_score(model, X_train, y_train, cv=cross_validation, scoring=scoring)
        results.append(cv_results)
        names.append(name)
        resume = (name, cv_results.mean(), cv_results.std())
        msg.append(resume)
    print(msg)

    # Compare results between algorithms
    fig = plt.figure()
    fig.suptitle('Comparison of algorithms with evaluation metrics: %s' %scoring)
    ax = fig.add_subplot(111)
    ax.set_xlabel('Candidate models')
    ax.set_ylabel('%s' %scoring)
    plt.boxplot(results)
    ax.set_xticklabels(names)
    plt.show()

    results = []


# In[45]:


print("la balanced_accuracy tient compte du déséquilibre de classe en donnant à chaque classe un poids égal dans le calcul.")
print("The model with the highest balanced_accuracy would be considered as performing better in terms of this evaluation metric.")
print("So, XGB seems to perform better in terms of this evaluation metric")


# ## *7. Adjust hyperparameters*.
# 
# Steps to perform the hyperadjustment of the parameters:
# 
# * Metric to optimize
# * Define search parameter ranges: *params*
# * Train with validation data: *X_val
# 
# [XGBClassifier]:https://xgboost.readthedocs.io/en/latest/parameter.html

# In[46]:


from sklearn.model_selection import TimeSeriesSplit
model =  xgb.XGBClassifier()    ### your code here
params = {
     'booster': ['gbtree', 'dart'], #default=gbtree
     'eta': [0.1, 0.3], #default=0.3
     # 'max_depth': [3, 6, 8],  #default=6
     #'predictor': ['auto', 'gpu_predictor'] # default auto
 }
scoring='balanced_accuracy'     ### your code here METRIC TO OPTIMIZE
cross_validation = TimeSeriesSplit(n_splits=10)      ### your code here
my_cv = cross_validation.split(X_test, y_test)
gsearch = GridSearchCV(estimator=model, param_grid=params, scoring=scoring, cv=my_cv, verbose=2)
gsearch.fit(X_test, y_test)

print("Best result: %f using the following hyperparameters %s" % (gsearch.best_score_, gsearch.best_params_))
means = gsearch.cv_results_['mean_test_score']
stds = gsearch.cv_results_['std_test_score']
params = gsearch.cv_results_['params']


# ## *8.  Final evaluation of the model*
# 
# 

# Evaluation metrics:
#   * 1. Confusion matrix
#   * 2. Matthews Coefficient
# 
#     
# **Train the model with the optimal hyperparameters found in the previous section and make the predictions**. 

# In[47]:


finalModel =  xgb.XGBClassifier(**gsearch.best_params_)    ### your code here

finalModel.fit(X_train,y_train)  
y_predict = finalModel.predict(X_test)  


# In[48]:


pip install --upgrade scikit-learn


# **1. Confusion matrix**

# In[53]:


#from sklearn.metrics import confusion_matrix, classification_report, plot_confusion_matrix
import matplotlib.pyplot as plt
#from sklearn.metrics import confusion_matrix, plot_confusion_matrix
#from sklearn.model_selection import train_test_split
#from sklearn.datasets import make_classification
#from sklearn.svm import SVC
confusion_matrix = confusion_matrix(y_test, y_predict) ### your code here


# In[58]:


print(classification_report(y_test, y_predict))
print(confusion_matrix)


# In[56]:


# Non-normalized graph of the martiz of confusion

disp = plot_confusion_matrix(finalModel, X_test, y_test,
                                 cmap=plt.cm.Blues, values_format = '')


# **2. Matthews Coeficient (MCC)**
# 
# The MCC uses correlation coefficients between -1 and +1. 
# * Coefficient +1 represents a perfect prediction.
# * Coefficient 0 represents a random mean prediction.
# * Coefficient -1 represents an inverse prediction. 

# In[59]:


from sklearn.metrics import matthews_corrcoef

### your code here
matthews_coefficient = matthews_corrcoef(y_test, y_predict)
print("Matthews Coefficient:", matthews_coefficient)


# In[ ]:




