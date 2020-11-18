import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
# from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

markdown_text = '''

The gender wage gap is a real and impactful phenomenon that is still present in the United States. 
According to some studies, women only make 82 cents to the dollar that a man makes. This has makes it 
harder for women to pay back loans, save for retirement, buy houses, and more. The lower lifetime earnings
also result in lower social security checks in retirement. This is a real issue that must be addressed. 
(https://www.aauw.org/resources/research/simple-truth/)

The General Social Survey has collected data on hundreds of trends across American society since 1972, while 
some of these go back up to 80 years. This is a great source for seeing and understanding sociological trends in
American society. GSS also supports data transparency and makes the data freely available. We will use this data
to analyze the gender wage gap in the United States. More information about the General Social Survey can be found
here: http://www.gss.norc.org/About-The-GSS.


'''

avgs = gss_clean.groupby('sex').agg({'income':'mean', 'job_prestige': 'mean', 'socioeconomic_index': 'mean', 'education':'mean'}).round(2)
avgs = avgs.reset_index().rename({'income':'Income', 'job_prestige':'Occupational Prestige', 'socioeconomic_index':'Socioeconomic Index', 'education':'Years of Education', 'sex':'Sex'}, axis=1)

table = ff.create_table(avgs)

gss_clean.male_breadwinner = gss_clean.astype('category').male_breadwinner.cat.reorder_categories(['strongly disagree', 'disagree', 'agree', 'strongly agree'])
bars = pd.DataFrame(gss_clean.groupby(['sex', 'male_breadwinner']).size()).reset_index().rename({'sex':'Sex', 'male_breadwinner':'Male Breadwinner?', 0:'Count'}, axis=1)
barplot = px.bar(bars, x='Male Breadwinner?', y='Count', color='Sex', barmode='group',
      labels={'Count':'Number of Responses', 'Male Breadwinner?':'Response to Question about Males being Breadwinners'})

fig = px.scatter(gss_clean, x='job_prestige', y='income', color='sex', 
                trendline='ols',
                hover_data=['education', 'socioeconomic_index'],
                labels={'job_prestige':'Occupational Prestige', 'income':'Income'})

fig2 = px.box(gss_clean, x='income', y='sex', color='sex',
             labels={'income':'Income', 'sex':''})
fig2.update_layout(showlegend=False)

fig3 = px.box(gss_clean, x='job_prestige', y='sex', color='sex',
             labels={'job_prestige':'Occupational Prestige', 'sex':''})
fig3.update_layout(showlegend=False)

data = gss_clean[['income', 'sex', 'job_prestige']]
data['Prestige_Bin'] = pd.cut(data.job_prestige, bins=6, labels=['Very Low', 'Low', 'Medium-Low', 'Medium-High', 'High', 'Very High'])
data = data.dropna(axis=0, how='any')
data.Prestige_Bin = data.Prestige_Bin.cat.reorder_categories(['Very Low', 'Low', 'Medium-Low', 'Medium-High', 'High', 'Very High'])

fig4 = px.box(data, x='income', y='sex', color='sex', color_discrete_map={'male':'red', 'female':'green'},
             facet_col='Prestige_Bin', facet_col_wrap=2, 
              category_orders={'Prestige_Bin':['Very Low', 'Low', 'Medium-Low', 'Medium-High', 'High', 'Very High']},
              labels={'income':'Income', 'sex':'Sex'}
             )

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(
    [
        html.H1("Understanding the Gender Wage Gap"),
        
        dcc.Markdown(children = markdown_text),
        
        html.H2("Mean Statistics table by Sex"),
        dcc.Graph(figure=table),
        
        html.H2("Male Breadwinner Response by Sex"),
        dcc.Graph(figure=barplot),
        
        html.H2("Occupational Prestige vs. Income by Sex"),
        dcc.Graph(figure=fig),
        
        html.H2("Income Box Plots by Sex"),
        dcc.Graph(figure=fig2),
        
        html.H2("Occupational Prestige Box Plots by Sex"),
        dcc.Graph(figure=fig3),
        
        html.H2("Grouped Occupational Prestige Box Plots by Sex"),
        dcc.Graph(figure=fig4)
        
        
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)


