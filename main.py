import streamlit as st 
import pandas as pd 

import plotly.graph_objects as go
import plotly.express as px

import datetime
from datetime import datetime as dt

sd = st.sidebar
st.set_page_config(layout='wide',page_title='Attendance')

skip_days_df = pd.read_csv('HL.csv')

def string_to_datetime(date):
        return dt.strptime(date, '%Y-%m-%d')

def CollegeHoliday(college_holidays,date):
        for n in college_holidays[5]:
            startdate, enddate = n
            startdate , enddate  = string_to_datetime(date = startdate) , string_to_datetime(date = enddate)
            if startdate.date() <= date < enddate.date(): return True

def getdiff(attend,conduct,perce):
    if len(sim_df) > 0:
        lastrow = sim_df.iloc[-1]
        lastperc = lastrow['Percentage'].tolist()
        # print('-'*10)
        return round(perce - lastperc,3)
    else:
        
        prev = sim_starting_classes_attended_input/ sim_starting_conducted_classes_input

        return round((attend/conduct - prev)*100,3)
    
def getholidays():
    return list(map(string_to_datetime,pd.read_csv('HL.csv')['Dates'].tolist()))
 
a = st.columns(4)
with a[0]:
    sim_starting_date_input = sd.date_input(
        'Select first date', dt.today())
with a[1]:
    sim_starting_classes_attended_input = sd.number_input(
        'Classes attended', value=1,min_value=1)
with a[2]:
    sim_starting_conducted_classes_input = sd.number_input(
        'Classes conducted', value=1,min_value=1)
with a[3]:
    sim_Ending_date_input = sd.date_input(
        'Select Final date', sim_starting_date_input + datetime.timedelta(days=1))
    
sd.divider()

if 'leaves' not in st.session_state:
     st.session_state['leaves'] = []

newldate = sd.date_input('Select Leave date', dt.today())

if sd.button('Add leave'):
    if newldate not in st.session_state['leaves']:
        st.session_state['leaves'].append(newldate)
if sd.button('Remove Leave'):
    if newldate in st.session_state['leaves']:
        st.session_state['leaves'].remove(newldate)
    else:
        sd.warning("Date is not listed in leaves")


if st.session_state['leaves']:
    with sd.expander("Leaves"):
         st.write(*st.session_state['leaves'])

if st.session_state['leaves'] and sd.button('Clear leaves'):
    st.session_state['leaves'] = []
    st.rerun()
    
sim_date = sim_starting_date_input
sim_Total_classes_attended = sim_starting_classes_attended_input
sim_Total_Conducted_classes = sim_starting_conducted_classes_input
sim_end_date = sim_Ending_date_input

sim_df = pd.DataFrame(
        columns=["Date", "Total_classes_attended", "Total_Conducted_classes", "Percentage","Change"])

holidays = getholidays()

college_holidays = {
    3: [],
    4 : [['2023-05-15','2023-06-05']],
    5 : [['2023-10-22','2023-10-26']]
}

while sim_date <= sim_end_date or len(sim_df) < 1:
    if sim_date.weekday() != 6 and sim_date not in holidays and not CollegeHoliday(college_holidays,sim_date):
        if sim_date not in st.session_state['leaves']:
            sim_Total_classes_attended +=  7
        sim_Total_Conducted_classes += 7
        sim_percentage = (sim_Total_classes_attended /
                            sim_Total_Conducted_classes) * 100

        diff = getdiff(sim_Total_classes_attended,sim_Total_Conducted_classes,sim_percentage)
        sim_df = pd.concat([sim_df, pd.DataFrame({
            "Date": [sim_date],
            "Total_classes_attended": [sim_Total_classes_attended],
            "Total_Conducted_classes": [sim_Total_Conducted_classes],
            "Percentage": [sim_percentage],'Change' : [diff]})],
            ignore_index=True)

    sim_date += datetime.timedelta(days=1)

st.dataframe(sim_df,use_container_width=True)

with st.expander('Graphs'): 
    pcolor = None      
    dfdata = sim_df 
    fig = px.line(dfdata, x='Date', y='Percentage',
                    title=f"Simulated Attendance percentage : {round(dfdata['Percentage'].tolist()[-1],2)}", markers=True, template='plotly_dark', color_discrete_sequence=[pcolor])
    fig.update_xaxes(showgrid=False, showline=True,
                        linecolor=pcolor, showspikes=True)
    fig.update_yaxes(showgrid=False, range=[
                        0, 100], color=pcolor, showline=True, linecolor=pcolor, autorange=True, showspikes=True)
    fig.update_layout(
        #         annotations=[
        #     dict(x=0.5,y=100,xref="paper",yref="y",text="Goal: 100%",showarrow=False,font=dict(size=14)),
        #     dict(x=0.5,y=75,xref="paper",yref="y",text="Warning: 75%",showarrow=False,font=dict(size=14))
        # ],
        shapes=[
            dict(
                type="line",
                x0=0,
                y0=75,
                x1=1,
                y1=75,
                xref="paper",
                yref="y",
                line=dict(
                    color="#2ECC71",
                    width=2
                )
            ),
            dict(
                type="line",
                x0=0,
                y0=65,
                x1=1,
                y1=65,
                xref="paper",
                yref="y",
                line=dict(
                    color="#F05959",
                    width=2
                )
            )
        ]
    )
    st.plotly_chart(fig, use_container_width=True)



    colors = ['green' if change >= 0 else 'red' for change in dfdata[dfdata.columns[-1]]]
    fig = go.Figure(data=[go.Bar(
        x=dfdata['Date'],
        y=dfdata[dfdata.columns[-1]],
        marker_color=colors
    )])

    fig.update_layout(
        title='Attendance Change in Fifth Semester',
        xaxis_title='Date',
        yaxis_title='Percentage Change in Attendance'
    )

    fig.update_xaxes(showspikes=True)
    fig.update_yaxes(showspikes=True)

    st.plotly_chart(fig, use_container_width=True)