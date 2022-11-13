        
from dash import Dash, html, Input, Output, dash_table
import pandas as pd
import pandas as pd
import PyPDF2

pdfFileObj = open('dab_106.pdf', 'rb')
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)


# In[109]:


# create page object and extract text
pageObj = pdfReader.getPage(3)
page1 = pageObj.extractText()
page_blob = pageObj.extractText()


output = ""
for i in range(pdfReader.numPages):
    pageObj = pdfReader.getPage(i)
    output += pageObj.extractText()




page1 = output

course_name = page1.replace('\n \n',', ').replace('\n','')
course_name = course_name.split('Course Outline')
course_name = course_name[1].split('Page  1')
course_name = course_name[0]
course_name

# strip away page header
page1 = page1[25:]

# insert commas to separate variables and then remove excess strings
page1 = page1.replace('\n \n',', ').replace('\n','')

page1 = page1.split(',')

s = pd.Series(page1)
out = (s.str.extractall(r'(?P<Object>Assignments|Exam 1|Exam 2|Exam 3|Exam|Project|Quizzes|Final Exam)|(?P<Weight>\d+.00)|(?P<Frequency>Frequency: \d+)')
       .groupby(level=0).first()
       )
df = pd.DataFrame(out)



'''out = (pd.Series(page1)
       .str.extract(r'(?P<Weight>\d+.00%)\W*(?P<Object>\w+)')
       .dropna(subset='Object')
      )

print(out)'''


df['Frequency'] = df.Frequency.shift(-1)

df = df.dropna()

df['Frequency'] = df['Frequency'].str.extract('(\d+)').astype(int)
df['Weight'] = df['Weight'].astype(float)


df['Weight per Object'] = df.Weight/df.Frequency

df['Flag'] = ((df['Object'].str.contains('Quiz', regex=True)) & (abs(df['Weight per Object']) <= 4)) | ((df['Object'].str.contains('Exam', regex=True)) & (df['Weight per Object'] >= 25) & (df['Weight per Object'] <= 40)) | ((df['Object'].str.contains('Test', regex=True)) & (df['Weight per Object'] >= 5) & (df['Weight per Object'] <= 24))
#df['Description'] =  "This assessment has a weightage of " + df['Weight'] + " percentage"
df1 = df[df['Flag']==False]
df1 = df1[['Object', 'Weight', 'Flag']]


##########################################################

output = ""
for i in range(pdfReader.numPages):
    pageObj = pdfReader.getPage(i)
    output += pageObj.extractText()
page1 = output

page1 = page1.replace('\n \n \n•','>>>').replace(')\n \n•', '>>>').replace('\n \n•', '>').replace('\n•','>').replace('\nEKS:', '')
page1 = page1.split('>>>')
#page1
del page1[0]
clo1 = page1[0].split('>')
sep = ' '
clo1_verbs = []
for i in range(len(clo1)):
    x = clo1[i].split(sep, 1)[0]
    clo1_verbs.append(x)
word_list = pd.read_excel('word_list.xlsx')
#word_list.head()

scores = []

for i in range(len(clo1_verbs)):
    if word_list['1'].str.contains(clo1_verbs[i]).any():
        scores.append(1)
    elif word_list['2'].str.contains(clo1_verbs[i]).any():
        scores.append(2)
    elif word_list['3'].str.contains(clo1_verbs[i]).any():
        scores.append(3)
    elif word_list['4'].str.contains(clo1_verbs[i]).any():
        scores.append(4)
    elif word_list['5'].str.contains(clo1_verbs[i]).any():
        scores.append(5)
    elif word_list['6'].str.contains(clo1_verbs[i]).any():
        scores.append(6)
    else:
        scores.append(0)

clo1_df = {'Verbs': clo1_verbs, 'Scores': scores}
clo1_df = pd.DataFrame(clo1_df)

clo1_df['Dist'] = abs(clo1_df['Scores'][0] - clo1_df['Scores'])

bloom_violations = clo1_df[clo1_df['Dist'] >= 2]
df2 = bloom_violations[['Verbs', 'Dist']][1:]

app = Dash(__name__)


app.layout = html.Div([
    html.H4('Validation Rules for Assessment'),
    html.H4('Quiz - 1% to 4%'),
    html.H4('Test - 5% to 24%'),
    html.H4('Exam 25% to 40%'),
    html.H4('CAE Violations found in ' + str(course_name)),
    html.P(id='table_out'),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} 
                 for i in df1.columns],
        data=df1.to_dict('records'),
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender")
    ),
    html.H4("EKS verb distance from CLO#1: " + str(clo1[0])),
    html.P(id='table_out1'),
    dash_table.DataTable(
        id='table1',
        columns=[{"name": i, "id": i} 
                 for i in df2.columns],
        data=df2.to_dict('records'),
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender")
    )
])

@app.callback(
    Output('table_out', 'children'), 
    Input('table', 'active_cell'))
    
@app.callback(
    Output('table_out1', 'children'), 
    Input('table1', 'active_cell'))
    
def update_graphs(active_cell):
    if active_cell:
        cell_data = df1.iloc[active_cell['row']][active_cell['column_id']]
        cell_data2 = df2.iloc[active_cell['row']][active_cell['column_id']]
        return cell_data, cell_data2

        #return f"Data: \"{cell_data}\" from table cell: {active_cell}"
    #return "Click the table"
app.run_server(debug=True, port=8051)