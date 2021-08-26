import streamlit as st
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import plotly.express as ex
import math
import plotly.graph_objects as go
from statistics import mode
from scipy import stats

def app():
    st.title('General Information about your dataset')
    st.markdown('Here you able to find information about your dataset just upload')

    uploaded_file = st.sidebar.file_uploader('Upload the raw data here', type=['xlsx'])
    sheet_name = st.sidebar.text_input('Please enter the sheet name where the data is in')

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

    question_begins = st.sidebar.slider('Please tell me when the questions begin', min_value=0, max_value=len(list(df.columns)))
    beginging = question_begins - 1

    liste_columns = list(df.columns)[beginging:]
    liste_columms_new = []
    for a in liste_columns:
        liste_columms_new.append(a.split(' - ')[0])

    count={}
    for item in liste_columms_new:
        count[item]=liste_columms_new.count(item)

    liste_new = []
    for i in range(len(list(count.values()))):
        if np.array(list(count.values())[i]) > 1:
            liste_new.append(list(count.keys())[i])

    liste_new_new = []
    for q in range(len(liste_new)):
        liste_new_new.append([i for i in liste_columns if liste_new[q] in i])

    if len(liste_new_new) > 0:
        for a in liste_new_new:
             df = df.drop(a, axis=1)

    st.dataframe(df)

    st.markdown('your dataframe has '+ str(len(df)) +' rows and '+ str(len(df.columns))+' columns')

    #filter_data(filter)

    visuals = st.button('Visualize every question')

    if visuals:
        Visual_columns = list(df.columns)[beginging:]
        for x in Visual_columns:
            for i in range(len(Visual_columns)):
                plt.figure(figsize=(25,10))
                fig = ex.bar(df[x].value_counts(), title=str(i)+'th Question')
                st.plotly_chart(fig)

    
    range_question = st.button('Range_per_question')
    min_value = []
    max_value = []
    range_values=[]
    if range_question:
        Visual_columns = list(df.columns)[beginging:]
        for i in Visual_columns:
            min_value.append(df[i].min())
            max_value.append(df[i].max())
        
        for k in range(len(min_value)):
                range_values.append(str(min_value[k])+' - '+str(max_value[k]))

        dict_range_values = dict(zip(Visual_columns, range_values))
        dataframe_range = pd.DataFrame.from_dict(dict_range_values, orient='index')
        st.dataframe(dataframe_range)        
        
    modal = st.button('Modal_value')
    model_values = []
    if modal:
        Visual_columns = list(df.columns)[beginging:]
        for i in Visual_columns:
            model_values.append(mode(list(df[i])))
        dict_modal_value = dict(zip(Visual_columns, model_values))
        dataframe = pd.DataFrame.from_dict(dict_modal_value, orient='index')
        st.dataframe(dataframe)

        #Visual_columns = list(df.columns)[beginging:]
        #columns_select = st.selectbox('Do you want to filter the data?', list(df.columns))
        #filtered_modal_values = []
        #for k in df[columns_select].unique():
            #for i in Visual_columns:
                #filtered_modal_values.append(mode(list(df[df[columns_select]==k][i])))
        #st.write(len(filtered_modal_values))

    Distribution = st.button('Distribution_per_question')
    count_values = []
    if Distribution:
        Visual_columns = list(df.columns)[beginging:]
        for i in Visual_columns:
            st.write(df[i].value_counts()/df[i].value_counts().sum()*100)




 #filter = st.sidebar.selectbox('If you want to filter your data please enter the columns', list(df.columns))
 #filter_specific = st.sidebar.multiselect('If you want to filter your data please enter the columns', list(df[filter].unique()))
 #df = df[df[filter].isin(list(filter_specific))]
 #df = df.sort_values(filter)
 #st.dataframe(df)