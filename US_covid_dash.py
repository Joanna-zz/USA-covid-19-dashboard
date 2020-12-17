#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 11:30:34 2020

@author: zqy
"""

"""
Solution to exercise #1 on Week 11
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

import requests
import datetime


'''state data'''
url='https://api.covidtracking.com/v1/states/daily.json'
params={}
covid_req=requests.get(url,params=params)
covid_req.raise_for_status()

covid=covid_req.json()



#only left the date before 20201201
covid1=[]
for item in covid:
    if item['date']<=20201215:
        covid1.append(item)

covid1


'''build dataframe'''
deaths=[]
states=[]
positive=[]
recovered=[]

for item in covid1:
    if item['date']==20201215:
        states.append(item['state'])
        deaths.append(item['death'])
        positive.append(item['positive'])
        recovered.append(item['recovered'])
    
covid_df=pd.DataFrame(index=states)
covid_df['positive']=positive
covid_df['death']=deaths
covid_df['recovered']=recovered

covid_df=covid_df.reset_index()
covid_df.columns=['code','positive','death','recovered']
covid_state=covid_df.groupby('code').sum().reset_index()

code=pd.read_csv('/Users/zqy/Desktop/code name.csv')
code=code.loc[:,['state','code']]

covid_state=pd.merge(code, covid_state)

##impute values of recovered number for several states that have missing values by checking the CDC
covid_state.iloc[4,4]=634033
covid_state.iloc[9,4]=381
covid_state.iloc[10,4]=927
covid_state.iloc[13,4]=87148
covid_state.iloc[25,4]=4102
covid_state.iloc[28,4]=148256
covid_state.iloc[47,4]=6378

covid_state['recovered']=covid_state['recovered'].astype(int)
##add a new variable--death rate
covid_state['death rate']=covid_state['death']/covid_state['positive']
covid_state[u'death rate'] = covid_state[u'death rate'].apply(lambda x: format(x, '.2%')) 

top10=covid_state.sort_values(by=['positive'],ascending=False)[:10]
top10=top10.sort_values(by=['positive'],ascending=False)
top10=top10[['state','positive']]


'''US overall data'''
'''the trend of US positive every month'''
url1='https://api.covidtracking.com/v1/us/daily.json'
params={}
US_req=requests.get(url1,params=params)
US_req.raise_for_status()

US=US_req.json()


#only left the date before 20201215
US1=[]
for item in US:
    if item['date']<=20201215:
        US1.append(item)

US1

US_pos=[]
US_death=[]
US_recovered=[]
US_dates=[]

for item in US1:
    US_pos.append(item['positive'])
    US_death.append(item['death'])
    US_recovered.append(item['recovered'])
    US_dates.append(item['date'])

US_covid=pd.DataFrame(index=US_dates)
US_covid['positive']=US_pos
US_covid['death']=US_death
US_covid['recovered']=US_recovered
US_covid

US_covid.fillna(value=0,inplace=True)
US_covid=US_covid.astype(int)
US_covid.index=pd.to_datetime(US_covid.index,format='%Y%m%d')
a=US_covid.reset_index().drop(['index'], axis=1)
b=US_covid.iloc[1:,].reset_index().drop(['index'], axis=1)
x=a-b
x.dropna(axis=0,inplace=True)
x=x.astype(int)
x.index=US_covid.index[:-1]

x=x.reset_index().drop(index=[8,186,249]) ##delete the outliers
x.columns=['date','positive','death','recovered']
x=x.set_index(['date'])
x1=x[['positive','recovered']]
x2=x[['death']]



stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# pandas dataframe to html table
def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

app = dash.Dash(__name__, external_stylesheets=stylesheet)

server = app.server

df = covid_state

options=[]
for i in list(covid_state.state):
    options.append({'label':i,'value':i})
    
fig1 = px.line(x1)
fig1.update_layout(title="Trend of New Cases and Recoveries in the USA",
                  xaxis_title="Date",
                  yaxis_title="Number of People",
                  legend_title="Condition",
                  font=dict(
                          family="Courier New, monospace",
                          size=14,
                          color="RebeccaPurple"))


fig2=px.line(x2)
fig2.update_layout(title="Trend of Death in the USA",
                  xaxis_title="Date",
                  yaxis_title="Number of People",
                  legend_title="Condition",
                  font=dict(
                          family="Courier New, monospace",
                          size=14,
                          color="RebeccaPurple"))

#fig3=fig = px.bar(top10,x='positive',y='state',color='positive')

app.layout = html.Div([
    html.H1('USA COVID-19 Dashboard', style={'textAlign': 'center'}),
    html.Br(),
   # html.Div([dcc.Graph(id='covid_fig',figure=fig1)]),
    html.Div([dcc.Graph(id='covid_fig1',figure=fig1)],
              style={'width': '49%', 'display': 'inline-block'}),
    html.Div([dcc.Graph(id='covid_fig2',figure=fig2)],
              style={'width': '49%', 'display': 'inline-block','float': 'right'}),
    html.Div(["NO.States: ", dcc.Input(placeholder='Enter # sides...',
                                   id='num_states', type='number', value=10)
              ],
             style={'width': '40%', 'display': 'inline-block'}
             ),
    html.Div([dcc.Graph(id='covid_fig3')]),
              
    html.Div([#html.H4(''),
              #dcc.Graph(id='covid_fig1',figure=fig1),
              
              html.H4('Number of states to display:'),
              dcc.Slider(id="num_row_slider", min=1, max=51,value=25,
              marks={i:str(i) for i in range(1,(len(df)+2),10)}),
                         
              html.H4('Sort table by:'),
              dcc.Dropdown(options=[{'label': 'state', 'value': 'state'},     
                                    {'label': 'positive', 'value': 'positive'},
                                    {'label': 'death', 'value': 'death'},
                                    {'label': 'recovered', 'value': 'recovered'},
                                    {'label': 'death rate', 'value': 'death rate'}],
                           id='sort_by_dropdown',
                           value='state'),
                                    
              #html.H4('State:'),
              #dcc.Input(placeholder='Enter a state name...', id='my-input', type='text', value=''),
              #html.H4('Output:'),
              #html.Div(id='my-output'),
              
              html.H4('Select states to display:'),
              dcc.Checklist(options=options,
                            #[{'label': 'California', 'value': 'California'},
                                     #{'label': 'Massachusetts', 'value': 'Massachusetts'},
                                     #{'label': 'New York', 'value': 'New York'}],
                           id="state_select_checklist",
                           value=list(covid_state.state))],
             style={'width': '49%', 'display': 'inline-block'}),
    html.Div(
             html.Div(id="df_div"),
             style={'width': '49%', 'display': 'inline-block', 'float': 'right'})
    ])

# Update the table
@app.callback(
    Output(component_id='df_div', component_property='children'),
    [Input(component_id='num_row_slider', component_property='value'),
     Input(component_id='state_select_checklist', component_property='value'),
     Input(component_id='sort_by_dropdown', component_property='value')]
)
def update_table(num_rows_to_show, states_to_display, sort_by):
    x = df[df.state.isin(states_to_display)].sort_values(sort_by, ascending=(sort_by == 'state'))
    return generate_table(x, max_rows=num_rows_to_show)

# Update the slider max
@app.callback(
    Output(component_id='num_row_slider', component_property='max'),
    [Input(component_id='state_select_checklist', component_property='value')]
)
def update_slider(states_to_display):
    x = df[df.state.isin(states_to_display)]
    return min(100, len(x))

'''
##Update the output
df_state=covid_state.set_index('state')
@app.callback(
    Output(component_id='my-output', component_property='children'),
    [Input(component_id='my-input', component_property='value')])

def update_output(input_value):
    positive =df_state[df_state.code == input_value].positive[0]
    return 'Positive:{} Death:{} Recovered:{} Death_rate:{}'.format(positive ,1,1,1)
'''
             

##Update the figure3                                                          
@app.callback(
    Output(component_id='covid_fig3', component_property='figure'),
    [Input(component_id='num_states', component_property='value'),]
)

def update_output_div(num_states):
    df1=top10.iloc[:num_states,:]
    fig3= px.bar(df1,x='positive',y='state',color='positive')
                      
    fig3.update_layout(title={'text':"Cases by Top 10 States in US",'y':0.95,'x':0.5,
                              'xanchor':'center','yanchor':'top'},
                      
                      xaxis_title="Positive Cases",
                      yaxis_title="State",
                      
                      font=dict(
                          family="Courier New, monospace",
                          size=16,
                          color="RebeccaPurple")
                      )

    return fig3


if __name__ == '__main__':
    app.run_server(debug=True)
    




