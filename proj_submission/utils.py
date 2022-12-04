import pandas as pd
import PyPDF2

def read_file(fname):
    pdfFileObj = open(fname, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    
    pageObj = pdfReader.getPage(3)
    page1 = pageObj.extractText()
    page_blob = pageObj.extractText()

    output = ""
    for i in range(pdfReader.numPages):
        pageObj = pdfReader.getPage(i)
        output += pageObj.extractText()
    
    page1 = output
    page1 = page1[25:]      
    '''
    # insert commas to separate variables and then remove excess strings
    page1 = page1.replace('\n \n',', ').replace('\n','')

    page1 = page1.split(',')'''
         
    return page1


def parse_course_name(page1):
    

    course_name = page1.replace('\n \n',', ').replace('\n','')
    course_name = course_name.split('Course Outline')
    course_name = course_name[1].split('Page  1')
    course_name = course_name[0]
    course_name

    return course_name


#rule for assessment weightage
def rule_1(page1):
    page1 = page1.replace('\n \n',', ').replace('\n','')
    page1 = page1.split(',')    
    s = pd.Series(page1)
    out = (s.str.extractall(r'(?P<Assesment>Assignments|Exam 1|Exam 2|Exam 3|Exam|Project|Quizzes|Final Exam)|(?P<Weight>\d+.00)|(?P<Frequency>Frequency: \d+)')
           .groupby(level=0).first()
           )
    df = pd.DataFrame(out)
    df['Frequency'] = df.Frequency.shift(-1)
    df = df.dropna()

    rules_df = pd.read_excel('rules.xlsx', 'id_1')
    a = int(rules_df.iloc[0:1,2:].values[0][0])
    b = int(rules_df.iloc[2:,1:2].values[0][0])
    c = int(rules_df.iloc[2:,2:].values[0][0])
    d = int(rules_df.iloc[1:2,1:2].values[0][0])
    e = int(rules_df.iloc[1:2,2:].values[0][0])
    
    
    
    df['Frequency'] = df['Frequency'].str.extract('(\d+)').astype(int)
    df['Weight'] = df['Weight'].astype(float)


    df['Weight per Assesment'] = df.Weight/df.Frequency
    '''
    Exam = "Exam is less than " + str(b) + "% or more than " + str(c) + "%"
    Quize = "Quiz weightage greater than " + str(d) + "%"
    Test = "Test is less than " + str(d) + "% or more than " + str(e) + "%"
    cols = ['Exam', 'Quize', 'Test']
    Rule_Violation = {"c1":cols,"Rules":[Exam,Quize,Test]}
    Rule_Violation = pd.DataFrame(Rule_Violation)'''
    list = []
    for i in df['Assesment']:
        if 'Exam' in i:
            list.append(rules_df[rules_df['assessment']=='Exam'].rules.to_string(index=False))
        elif 'Quiz' in i:
            list.append(rules_df[rules_df['assessment']=='Quiz']['rules'].to_string(index=False))
        elif 'Test' in i:
            list.append(rules_df[rules_df['assessment']=='Test']['rules'].to_string(index=False))
        else:
            list.append("Assessment name not found/Rule not defined")
    df['Violation'] = list

    df['Flag'] = ((df['Assesment'].str.contains('Quiz', regex=True)) & (df['Weight per Assesment'] <= a)) | ((df['Assesment'].str.contains('Exam', regex=True)) & (df['Weight per Assesment'] >= b) & (df['Weight per Assesment'] <= 40)) | ((df['Assesment'].str.contains('Test', regex=True)) & (df['Weight per Assesment'] >= 5) & (df['Weight per Assesment'] <= 24))
    #df['Description'] =  "This assessment has a weightage of " + df['Weight'] + " percentage"
    df1 = df[df['Flag']==False]
    df1 = df1[df1['Violation']!="Assessment name not found/Rule not defined"]
    df1 = df1[['Assesment', 'Weight', 'Frequency', 'Weight per Assesment', 'Violation']]
    return df1


##########################################################

#rule for cognitive domain - bloom's list
def rule_2_cd(page1):


    page1 = page1.replace('\n \n \n•','>>>').replace(')\n \n•', '>>>').replace('\n \n•', '>').replace('\n•','>').replace('\nEKS:', '').replace('\n \n \n', '>>>')
    page1 = page1.split('>>>')
    del page1[0]
    page1 = [c for c in page1 if "CLO" in c]
    i = 0
    sep = ' '
   
    for j in range(len(page1)):
        i += 1
        globals()["clo" + str(i)] = page1[j].split('>')
    i = 0
    sep = ' '


    for k in range(len(page1)):
        i += 1
        globals()["clo" + str(i) + "_verbs"] = []

    #i = 0
    z = 0
    for j in range(len(page1)):
        z += 1
        for k in range(len(globals()["clo" + str(z)])):
            i += 1
            x = globals()["clo" + str(z)][k].split(sep, 1)[0]
            globals()["clo" + str(z) + "_verbs"] .append(x)
    word_list = pd.read_excel('word_list.xlsx', 'cognitive_domain')
    clo_level = pd.read_excel('word_list.xlsx', 'levels')
    i = 0
    for k in range(len(page1)):
        i += 1
        globals()["scores" + str(i)] = []
    z = 0
    for j in range(len(page1)):
        z += 1
        for k in range(len(globals()["clo" + str(z) + "_verbs"])):
            if word_list['1'].str.contains(globals()["clo" + str(z) + "_verbs"][k]).any():
                globals()["scores" + str(z)].append(1)
            elif word_list['2'].str.contains(globals()["clo" + str(z) + "_verbs"][k]).any():
                globals()["scores" + str(z)].append(2)
            elif word_list['3'].str.contains(globals()["clo" + str(z) + "_verbs"][k]).any():
                globals()["scores" + str(z)].append(3)
            elif word_list['4'].str.contains(globals()["clo" + str(z) + "_verbs"][k]).any():
                globals()["scores" + str(z)].append(4)
            elif word_list['5'].str.contains(globals()["clo" + str(z) + "_verbs"][k]).any():
                globals()["scores" + str(z)].append(5)
            elif word_list['6'].str.contains(globals()["clo" + str(z) + "_verbs"][k]).any():
                globals()["scores" + str(z)].append(6)
            else:
                globals()["scores" + str(z)].append(0)
    z = 0
    for j in range(len(page1)):
        z += 1
        globals()['clo' + str(z) + '_df'] = {'EKS':globals()["clo" + str(z)],'Verbs': globals()["clo" + str(z) + "_verbs"], 'Scores': globals()["scores" + str(z)]}
        globals()['clo' + str(z) + '_df'] = pd.DataFrame(globals()['clo' + str(z) + '_df'])
    z = 0
    for j in range(len(page1)):
        z += 1
        globals()['clo' + str(z) + '_df']['Dist'] = (globals()['clo' + str(z) + '_df']['Scores'][0] - globals()['clo' + str(z) + '_df']['Scores'])
    z = 0
    for j in range(len(page1)):
        z += 1
        globals()['df' + str(z)] = globals()['clo' + str(z) + '_df'][['EKS','Verbs','Dist']][1:]
        
    z = 0
    for j in range(len(page1)):
        z += 1
        globals()['level' + str(z)] = clo_level[clo_level.level==int(globals()['clo' + str(z) + '_df'].Scores[0:1])].cognitive_domain.values[0]
    z = 0
    for j in range(len(page1)):
        z += 1
        globals()['clo' + str(z) + '_title'] = str(globals()['clo'+str(z)][0]) + "--CLO Level--" + str(globals()['level'+str(z)])
    '''    
    z = 0
    for j in range(len(page1)):
        z += 1
        return globals()['df' + str(z)], globals()['clo' + str(z) + '_title']'''
        
    return df1, df2, df3, df4, clo1_title, clo2_title, clo3_title, clo4_title
   

    
    

#Total number of CLOs

def page_len(page1):


    page1 = page1.replace('\n \n \n•','>>>').replace(')\n \n•', '>>>').replace('\n \n•', '>').replace('\n•','>').replace('\nEKS:', '').replace('\n \n \n', '>>>')
    page1
    page1 = page1.split('>>>')
    del page1[0]
    page1 = [c for c in page1 if "CLO" in c]
    return range(len(page1))



#rule for cognitive domain - psychomotor domain

def rule_2_pd(page1):


    page1 = page1.replace('\n \n \n•','>>>').replace(')\n \n•', '>>>').replace('\n \n•', '>').replace('\n•','>').replace('\nEKS:', '').replace('\n \n \n', '>>>')
    page1
    page1 = page1.split('>>>')
    del page1[0]
    page1 = [c for c in page1 if "CLO" in c]
    i = 0
    sep = ' '

    for j in range(len(page1)):
        i += 1
        globals()["clo" + str(i)] = page1[j].split('>')
    i = 0
    sep = ' '


    for k in range(len(page1)):
        i += 1
        globals()["clo" + str(i) + "_verbs"] = []

    #i = 0
    z = 0
    for j in range(len(page1)):
        z += 1
        for k in range(len(globals()["clo" + str(z)])):
            i += 1
            x = globals()["clo" + str(z)][k].split(sep, 1)[0]
            globals()["clo" + str(z) + "_verbs"].append(x)
    word_list = pd.read_excel('word_list.xlsx', 'psychomotor_domain')
    i = 0
    for k in range(len(page1)):
        i += 1
        globals()["scores" + str(i)] = []
    z = 0
    for j in range(len(page1)):
        z += 1
        for k in range(len(globals()["clo" + str(z) + "_verbs"])):
            if word_list['1'].str.contains(globals()["clo" + str(z) + "_verbs"][k]).any():
                globals()["scores" + str(z)].append(1)
            elif word_list['2'].str.contains(globals()["clo" + str(z) + "_verbs"][k]).any():
                globals()["scores" + str(z)].append(2)
            elif word_list['3'].str.contains(globals()["clo" + str(z) + "_verbs"][k]).any():
                globals()["scores" + str(z)].append(3)
            elif word_list['4'].str.contains(globals()["clo" + str(z) + "_verbs"][k]).any():
                globals()["scores" + str(z)].append(4)
            elif word_list['5'].str.contains(globals()["clo" + str(z) + "_verbs"][k]).any():
                globals()["scores" + str(z)].append(5)
            elif word_list['6'].str.contains(globals()["clo" + str(z) + "_verbs"][k]).any():
                globals()["scores" + str(z)].append(6)
            else:
                globals()["scores" + str(z)].append(0)
    z = 0
    for j in range(len(page1)):
        z += 1
        globals()['clo' + str(z) + '_df'] = {'EKS':globals()["clo" + str(z)],'Verbs': globals()["clo" + str(z) + "_verbs"], 'Scores': globals()["scores" + str(z)]}
        globals()['clo' + str(z) + '_df'] = pd.DataFrame(globals()['clo' + str(z) + '_df'])
    z = 0
    for j in range(len(page1)):
        z += 1
        globals()['clo' + str(z) + '_df']['Dist'] = (globals()['clo' + str(z) + '_df']['Scores'][0] - globals()['clo' + str(z) + '_df']['Scores'])
    z = 0
    for j in range(len(page1)):
        z += 1
        globals()['df' + str(z)] = globals()['clo' + str(z) + '_df'][['EKS','Verbs','Dist']][1:]

    return df1, df2, df3, df4, clo1_title, clo2_title, clo3_title, clo4_title
   
            
    
#####################################33

#rule for affective domain

def rule_2_ad(page1):


    page1 = page1.replace('\n \n \n•','>>>').replace(')\n \n•', '>>>').replace('\n \n•', '>').replace('\n•','>').replace('\nEKS:', '').replace('\n \n \n', '>>>')
    page1
    page1 = page1.split('>>>')
    del page1[0]
    page1 = [c for c in page1 if "CLO" in c]
    i = 0
    sep = ' '

    for j in range(len(page1)):
        i += 1
        globals()["clo" + str(i)] = page1[j].split('>')
    i = 0
    sep = ' '


    for k in range(len(page1)):
        i += 1
        globals()["clo" + str(i) + "_verbs"] = []

    #i = 0
    z = 0
    for j in range(len(page1)):
        z += 1
        for k in range(len(globals()["clo" + str(z)])):
            i += 1
            x = globals()["clo" + str(z)][k].split(sep, 1)[0]
            globals()["clo" + str(z) + "_verbs"] .append(x)
    word_list = pd.read_excel('word_list.xlsx', 'affective_domain')
    i = 0
    for k in range(len(page1)):
        i += 1
        globals()["scores" + str(i)] = []
    z = 0
    for j in range(len(page1)):
        z += 1
        for k in range(len(globals()["clo" + str(z) + "_verbs"])):
            if word_list['1'].str.contains(globals()["clo" + str(z) + "_verbs"][k]).any():
                globals()["scores" + str(z)].append(1)
            elif word_list['2'].str.contains(globals()["clo" + str(z) + "_verbs"][k]).any():
                globals()["scores" + str(z)].append(2)
            elif word_list['3'].str.contains(globals()["clo" + str(z) + "_verbs"][k]).any():
                globals()["scores" + str(z)].append(3)
            elif word_list['4'].str.contains(globals()["clo" + str(z) + "_verbs"][k]).any():
                globals()["scores" + str(z)].append(4)
            elif word_list['5'].str.contains(globals()["clo" + str(z) + "_verbs"][k]).any():
                globals()["scores" + str(z)].append(5)
            else:
                globals()["scores" + str(z)].append(0)
    z = 0
    for j in range(len(page1)):
        z += 1
        globals()['clo' + str(z) + '_df'] = {'EKS':globals()["clo" + str(z)],'Verbs': globals()["clo" + str(z) + "_verbs"], 'Scores': globals()["scores" + str(z)]}
        globals()['clo' + str(z) + '_df'] = pd.DataFrame(globals()['clo' + str(z) + '_df'])
    z = 0
    for j in range(len(page1)):
        z += 1
        globals()['clo' + str(z) + '_df']['Dist'] = (globals()['clo' + str(z) + '_df']['Scores'][0] - globals()['clo' + str(z) + '_df']['Scores'])
    z = 0
    for j in range(len(page1)):
        z += 1
        globals()['df' + str(z)] = globals()['clo' + str(z) + '_df'][['EKS','Verbs','Dist']][1:]

    return df1, df2, df3, df4, clo1_title, clo2_title, clo3_title, clo4_title
   
