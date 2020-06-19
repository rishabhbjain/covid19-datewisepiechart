import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import pandas as pd
from os.path import isfile

fileNamePickle = "allData.pkl"

def loadData(fileName):
    data = pd.read_csv(fileName)
    data.drop(
        ['iso_code', 'total_cases', 'total_deaths', 'new_deaths', 'total_cases_per_million', 'new_cases_per_million',
         'total_deaths_per_million', 'new_deaths_per_million', 'total_tests', 'new_tests', 'total_tests_per_thousand',
         'new_tests_per_thousand', 'new_tests_smoothed', 'new_tests_smoothed_per_thousand', 'tests_units',
         'stringency_index', 'population', 'population_density', 'median_age', 'aged_65_older', 'aged_70_older',
         'gdp_per_capita', 'extreme_poverty', 'cvd_death_rate', 'diabetes_prevalence', 'female_smokers', 'male_smokers',
         'handwashing_facilities', 'hospital_beds_per_100k'], axis=1, inplace=True)
    data = data.loc[data['location'] != 'World']
    data = data.loc[data['location'] != 'International']
    return data

def refreshData():
    allData = loadData("owid-covid-data.csv")
    allData.to_pickle(fileNamePickle)
    return allData

def allData():
    if not isfile(fileNamePickle):
        refreshData()
    allData = pd.read_pickle(fileNamePickle)
    return allData

def filtered_data(country):
    d = allData()
    data = d.loc[d['location'] == country]
    return data

countries = allData()['location'].unique()
countries.sort()

app = dash.Dash(__name__)

server = app.server

app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <title>Countrywise - Distribution of COVID - 19</title>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
       </footer>
    </body>
</html>"""

app.layout = html.Div(
    style={'font-family': "Courier New, monospace"},
    children=[
        html.H1('Datewise - Distribution of COVID-19 for each Country'),
        html.Div(className="row", children=[
            html.Div(className="two columns", children=[
                html.H5('Country'),
                dcc.Dropdown(
                    id='location',
                    value='Italy',
                    options=[{'label': c, 'value': c} for c in countries],
                )
            ]),
            dcc.Graph(id='indicator-pie')
        ])
    ]
)

def piechart(data):
    figure = go.Figure(data = [go.Pie(labels = data['date'], values = data['new_cases'])])
    figure.update_layout(autosize=False, width=1200, height=700, margin=dict(l=300, r=20, t=50, b=20))
    figure.update_traces(textposition='inside', textinfo='percent+label')
    return figure

@app.callback(
    Output('indicator-pie', 'figure'),
    [Input('location', 'value')]
)
def update_plots(location):
    data = filtered_data(location)
    pieChart = piechart(data)
    return pieChart

if __name__ == '__main__':
    allData()
    app.run_server(debug=True)
