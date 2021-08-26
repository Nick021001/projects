import streamlit as st 
import pandas as pd 
import numpy as np 
import seaborn as sns
import plotly.express as px
import base64
import itertools as it
from scipy import stats
from scipy.stats import chi2_contingency


def app():
    st.header('Data processing web app')
    st.subheader('This Web app helps you to get Reports and insights within a few minutes')

    #The Data input
    uploaded_file = st.sidebar.file_uploader('Upload the raw data here', type=['xlsx'])
    sheet_name = st.sidebar.text_input('Please enter the sheet name where the data is in')

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

    sort_value = st.sidebar.selectbox('Based on which Column do you want to sort the dataframe', list(df.columns))
    df = df.sort_values(sort_value) #damit am Ende die richtigen Werte im step 2 die richtigen Werte zugewiesen werden
    dataframe = df

    #double ids 

    duplicateRows = df.iloc[:,0].duplicated()
    if df[duplicateRows].shape[0] > 0:
        st.write("File contains duplicate response ids. Make sure you file is correct")
    else:
        st.write("No duplicate response ids found")


    #bereitstellen ab wann die Frage anfangen um Fragen von Custom Varibalen zu unterscheiden

    question_begins = st.sidebar.slider('Please tell me when the questions begin', min_value=0, max_value=len(list(df.columns)))
    beginging = question_begins - 1

    #Lösung für das Reserve One-hot-encoding alle fragen die Nomialskaliert sind werden entfernt 

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


    #Column für die Heatmap auswählen, basierend auf dem Column werden die Werte für die Heatmap generiert

    selected_columns = st.sidebar.multiselect('Please define the columns for the pivot table', list(df.columns))

    df_pivot = df.pivot_table(columns=selected_columns, aggfunc=['mean', 'count'])

    def filedownload(dataframe):
        csv = dataframe.to_csv()
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="Data.csv">Download CSV File</a>'
        return href

    st.dataframe(df_pivot)

    st.markdown(filedownload(df_pivot), unsafe_allow_html=True)

    splitBy = st.sidebar.selectbox('based on which columns do you want to create the heatmap', list(df.columns))
    heatmapColumns = list(df[splitBy].unique())

    #Liste mit Mittelwerten
    st.markdown('Please decide which statistical function do you want to use')

    average_with_std = st.button('average_with_std')
    average_value = st.button('average')
    ENPS = st.button('ENPS')
    Mean_per_question_block = st.button('average_per_question_block')
    correlation = st.button('correlation')
    T_test = st.button('T-Test')

    heatmapIndex = list(df.columns)[beginging:]
    categorical = st.sidebar.multiselect('Please enter the categorical columns', list(df.columns))
    #st.dataframe(dataframe[[categorical]])

    if average_value:
        heatmapData = {k:[df[df[splitBy] == k][x].mean() for x in heatmapIndex] for k in heatmapColumns}
        heatmap = pd.DataFrame(index=heatmapIndex, data=heatmapData)
        st.dataframe(heatmap)
        st.markdown(filedownload(heatmap), unsafe_allow_html=True)
    #dataframe mit den Werten erstellen
    #data_newer = pd.MultiIndex.from_frame(df[[categorical]])
    #for i in range(len(list(data_newer.columns))):
        #data_newer[list(data_newer.columns)[i]] = heatmapData[list(data_newer.columns)[i][1]]
    #st.dataframe(data_newer)


    if average_with_std:
        average = {k:[df[df[splitBy] == k][x].mean() for x in heatmapIndex] for k in heatmapColumns}
        std = {k:[df[df[splitBy] == k][x].std() for x in heatmapIndex] for k in heatmapColumns}

        range_with_var = []

        for x in heatmapColumns:
            for k in range(len(average[x])):
                range_with_var.append([average[x][k] - std[x][k], average[x][k] + std[x][k]])

        array = np.array(range_with_var)
        array = array.reshape(len(heatmapColumns),len(heatmapIndex), 2)

        dataframe = pd.DataFrame(index=heatmapIndex, columns=heatmapColumns)

        for i in range(len(heatmapColumns)):
            dataframe[heatmapColumns[i]] = array[i].tolist()

        list_all_values = [list(df[df[splitBy]==k][x]) for k in heatmapColumns for x in heatmapIndex]

        array_all_values = np.array(list_all_values)

        array_all_values = array_all_values.reshape(len(heatmapColumns), len(heatmapIndex))

        final_values = []
        for k in range(len(heatmapColumns)):
            for i in range(len(heatmapIndex)):
                final_values.append(100 * len([x for x in array_all_values[k][i] if x < list(list(dataframe[heatmapColumns[k]][i]))[0] or x > list(list(dataframe[heatmapColumns[k]][i]))[1]]) / len(array_all_values[k][i]))

        array_final_values = np.array(final_values)
        array_final_values = array_final_values.reshape(len(heatmapColumns), len(heatmapIndex))

        columns_adapted = []
        for i in heatmapColumns:
            columns_adapted.append(str(i)+' , '+'% values in average and variance')

        dataframe_adapted = pd.DataFrame(index=heatmapIndex, columns=columns_adapted)

        for i in range(len(columns_adapted)):
            dataframe_adapted[columns_adapted[i]] = array_final_values[i]

        final_dataframe = dataframe.join(dataframe_adapted)

        sorted_columns_list = sorted(list(final_dataframe.columns))

        final_dataframe = final_dataframe[sorted_columns_list]

        st.write(final_dataframe)
        st.markdown(filedownload(final_dataframe), unsafe_allow_html=True)
        


    ENPS_question = st.sidebar.selectbox('Please select the ENPS Question' ,list(df.columns))
    ENPS_columns = st.sidebar.selectbox('Based on which column do you want to build the ENPS Score',list(df.columns))

    Question_blocks = st.sidebar.multiselect('Please enter the every question belonging to a certain question block', list(df.columns))
    Question_blocks = list(Question_blocks)

    if Mean_per_question_block:
        heatmapData = {k:np.array(sorted(it.chain(*df[df[splitBy]==k][Question_blocks].values))).mean() for k in heatmapColumns}
        Heatmap = pd.DataFrame.from_dict(heatmapData, orient='index')
        st.dataframe(Heatmap)
        st.markdown(filedownload(Heatmap), unsafe_allow_html=True)
    
    if correlation:
        arr_correlation = []
        for i in heatmapIndex:
            liste = df[[i, ENPS_question]].corr()
            arr = np.array(liste)
            arr_correlation.append(arr[0][1])
            #st.write(arr_correlation)

        dict_correlation = {}
        for i in range(len(heatmapIndex)):
           dict_correlation[heatmapIndex[i]] = arr_correlation[i]

        df_corr = pd.DataFrame.from_dict(dict_correlation, orient='index')
        st.dataframe(df_corr)

    if T_test:
        dict_variable_with_values = {k:{x:np.array(df[df[splitBy] == k][x].values) for x in heatmapIndex} for k in heatmapColumns}
        dict_question_total_mean = {x:df[x].mean() for x in heatmapIndex}
            
        dict_ttest_results = {}
        for y in heatmapColumns:
                dict_ttest_results[y] = {z:list(stats.ttest_1samp(dict_variable_with_values[y][z], popmean = dict_question_total_mean[z])) for z in heatmapIndex}

        ttest_dataframe = pd.DataFrame.from_dict(dict_ttest_results, orient='index')
        st.dataframe(ttest_dataframe)

    if ENPS:
        #st.selectbox('What', [1,2,3])
        scores = []
        for i in df[ENPS_columns].unique():
            scores.append(df[df[ENPS_columns]==i][ENPS_question])

    promoters = []
    passives = []
    detractors = []
    nps = []
    for k in range(len(scores)):
        promoters.append([s for s in scores[k] if s >=10 and s <=11])
        passives.append([s for s in scores[k] if s >=8 and s <=9])
        detractors.append([s for s in scores[k] if s >=1 and s <=7])
        nps.append(float(len(promoters[k]) - len(detractors[k])) / len(scores[k]) * 100.0)
    
    heatmap_enps = dict(zip(list(df[ENPS_columns].unique()), nps))
    dataframe_heatmap_enps = pd.DataFrame.from_dict(heatmap_enps, orient='index', columns=['ENPS']) 
    dataframe_heatmap_enps['Promoter'] = [float(len(promoters[k]))/len(scores[k]) for k in range(len(scores))]
    dataframe_heatmap_enps['Passives'] = [float(len(passives[k]))/len(scores[k]) for k in range(len(scores))]
    dataframe_heatmap_enps['Detractors'] = [float(len(detractors[k]))/len(scores[k]) for k in range(len(scores))]
    st.dataframe(dataframe_heatmap_enps)
    st.markdown(filedownload(dataframe_heatmap_enps), unsafe_allow_html=True)
    

    #Excel datei erstellen
    writer = pd.ExcelWriter('Output.xlsx')
    dataframe.to_excel(writer, sheet_name='Raw Data')
    df_pivot.to_excel(writer, sheet_name='Pivot_table')
    #data_newer.to_excel(writer, sheet_name='Heatmap mit Mittelwerten')
    writer.close()



#{x:np.average(df[df['Ressort']=x][k].unique, weights=list(dict(heatmap_data_test[x][k][0]).values() for k in heatmap_data for x in heat_map_split_by)) for k in heatmap_data}