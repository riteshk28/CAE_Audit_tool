        
from dash import Dash, html, Input, Output, dash_table
import pandas as pd
import pandas as pd
import PyPDF2
import colorlover
import rules
from dash_style import discrete_background_color_bins

pdfFileObj = open('dab_502.pdf', 'rb')
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


##########################################

df1 = rules.rule_1(page1)

pageObj = pdfReader.getPage(2)
page1 = pageObj.extractText()
page_blob = pageObj.extractText()
page1
    
df2, df3, clo1, clo2 = rules.rule_2(page1)



##########################################
app = Dash(__name__)


cols = ['Dist']
(styles, legend) = discrete_background_color_bins(df2, columns = cols)
(styles1, legend) = discrete_background_color_bins(df3, columns = cols)

app.layout = html.Div([
    #html.H4('Validation Rules for Assessment'),
    #html.H4('Quiz - 1% to 4%'),
    #html.H4('Test - 5% to 24%'),
    #html.H4('Exam 25% to 40%'),
    html.H4('Course Name: ' + str(course_name)),
    html.P(id='table_out'),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} 
                 for i in df1.columns],
        data=df1.to_dict('records'),
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender"),
        fill_width=False
    ),
    html.H4("CLO: " + str(clo1[0])),
    html.P(id='table_out1'),
    dash_table.DataTable(
        id='table1',
        columns=[{"name": i, "id": i} 
                 for i in df2.columns],
        data=df2.to_dict('records'),
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender"),
        fill_width=False,
        style_data_conditional = styles
    ),
        html.H4("CLO: "+ str(clo2[0])),
    html.P(id='table_out2'),
    dash_table.DataTable(
        id='table2',
        columns=[{"name": i, "id": i} 
                 for i in df3.columns],
        data=df3.to_dict('records'),
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender"),
        fill_width=False,
        style_data_conditional = styles1
    )
])

@app.callback(
    Output('table_out', 'children'), 
    Input('table', 'active_cell'))
    
@app.callback(
    Output('table_out1', 'children'), 
    Input('table1', 'active_cell'))
    
@app.callback(
    Output('table_out2', 'children'), 
    Input('table2', 'active_cell'))
    
def update_graphs(active_cell):
    if active_cell:
        cell_data = df1.iloc[active_cell['row']][active_cell['column_id']]
        cell_data2 = df2.iloc[active_cell['row']][active_cell['column_id']]
        cell_data3 = df3.iloc[active_cell['row']][active_cell['column_id']]
        return cell_data, cell_data2, cell_data3

        #return f"Data: \"{cell_data}\" from table cell: {active_cell}"
    #return "Click the table"
app.run_server(debug=True)