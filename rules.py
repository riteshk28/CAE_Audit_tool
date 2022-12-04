import pandas as pd
import PyPDF2




#rule for assessment weightage
def rule_1(page1):
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
    Exam = "Exam is less than " + str(b) + "% or more than " + str(c) + "%"
    Quize = "Quiz weightage greater than " + str(d) + "%"
    Test = "Test is less than " + str(d) + "% or more than " + str(e) + "%"
    cols = ['Exam', 'Quize', 'Test']
    Rule_Violation = {"c1":cols,"Rules":[Exam,Quize,Test]}
    Rule_Violation = pd.DataFrame(Rule_Violation)
    list = []
    for i in df['Assesment']:
        if 'Exam' in i:
            list.append(Rule_Violation[Rule_Violation['c1']=='Exam']['Rules'].to_string(index=False))
        elif 'Quize' in i:
            list.append(Rule_Violation[Rule_Violation['c1']=='Quize']['Rules'].to_string(index=False))
        elif 'Test' in i:
            list.append(Rule_Violation[Rule_Violation['c1']=='Test']['Rules'].to_string(index=False))
        else:
            list.append("Assessment name not found/Rule not defined")
    df['Violation'] = list

    df['Flag'] = ((df['Assesment'].str.contains('Quiz', regex=True)) & (df['Weight per Assesment'] <= a)) | ((df['Assesment'].str.contains('Exam', regex=True)) & (df['Weight per Assesment'] >= b) & (df['Weight per Assesment'] <= 40)) | ((df['Assesment'].str.contains('Test', regex=True)) & (df['Weight per Assesment'] >= 5) & (df['Weight per Assesment'] <= 24))
    #df['Description'] =  "This assessment has a weightage of " + df['Weight'] + " percentage"
    df1 = df[df['Flag']==False]
    df1 = df1[['Assesment', 'Weight', 'Violation']]
    return df1


##########################################################

#rule for cognitive domain - bloom's list
def rule_2_cd(page1):


    page1 = page1.replace('\n \n \n•','>>>').replace(')\n \n•', '>>>').replace('\n \n•', '>').replace('\n•','>').replace('\nEKS:', '')
    page1
    page1 = page1.split('>>>')
    del page1[0]
    i = 0
    for j in range(len(page1)):
        i += 1
        globals()["clo" + str(i)] = page1[j].split('>')

    sep = ' '
    clo1_verbs = []
    for i in range(len(clo1)):
        x = clo1[i].split(sep, 1)[0]
        clo1_verbs.append(x)
        
    clo2_verbs = []
    for i in range(len(clo2)):
        x = clo2[i].split(sep, 1)[0]
        clo2_verbs.append(x)

    word_list = pd.read_excel('word_list.xlsx', 'cognitive_domain')
    scores1 = []

    for i in range(len(clo1_verbs)):
        
        if word_list['1'].str.contains(clo1_verbs[i]).any():
            scores1.append(1)
        elif word_list['2'].str.contains(clo1_verbs[i]).any():
            scores1.append(2)
        elif word_list['3'].str.contains(clo1_verbs[i]).any():
            scores1.append(3)
        elif word_list['4'].str.contains(clo1_verbs[i]).any():
            scores1.append(4)
        elif word_list['5'].str.contains(clo1_verbs[i]).any():
            scores1.append(5)
        elif word_list['6'].str.contains(clo1_verbs[i]).any():
            scores1.append(6)
        else:
            scores1.append(0)
            
    scores2 = []

    for i in range(len(clo2_verbs)):
        if word_list['1'].str.contains(clo2_verbs[i]).any():
            scores2.append(1)
        elif word_list['2'].str.contains(clo2_verbs[i]).any():
            scores2.append(2)
        elif word_list['3'].str.contains(clo2_verbs[i]).any():
            scores2.append(3)
        elif word_list['4'].str.contains(clo2_verbs[i]).any():
            scores2.append(4)
        elif word_list['5'].str.contains(clo2_verbs[i]).any():
            scores2.append(5)
        elif word_list['6'].str.contains(clo2_verbs[i]).any():
            scores2.append(6)
        else:
            scores2.append(0)

    clo1_df = {'EKS':clo1, 'Verbs': clo1_verbs, 'Scores': scores1}
    clo1_df = pd.DataFrame(clo1_df)

    clo2_df = {'EKS':clo2, 'Verbs': clo2_verbs, 'Scores': scores2}
    clo2_df = pd.DataFrame(clo2_df)


    clo1_df['Dist'] = abs(clo1_df['Scores'][0] - clo1_df['Scores'])

    clo2_df['Dist'] = abs(clo2_df['Scores'][0] - clo2_df['Scores'])

    df2 = clo1_df[['EKS','Verbs','Dist']][1:]
    df3 = clo2_df[['EKS','Verbs','Dist']][1:]


    return df2, df3, clo1, clo2
    


#rule for cognitive domain - psychomotor domain

def rule_2_pd(page1):


    page1 = page1.replace('\n \n \n•','>>>').replace(')\n \n•', '>>>').replace('\n \n•', '>').replace('\n•','>').replace('\nEKS:', '')
    page1
    page1 = page1.split('>>>')
    del page1[0]
    i = 0
    for j in range(len(page1)):
        i += 1
        globals()["clo" + str(i)] = page1[j].split('>')

    sep = ' '
    clo1_verbs = []
    for i in range(len(clo1)):
        x = clo1[i].split(sep, 1)[0]
        clo1_verbs.append(x)
        
    clo2_verbs = []
    for i in range(len(clo2)):
        x = clo2[i].split(sep, 1)[0]
        clo2_verbs.append(x)

    word_list = pd.read_excel('word_list.xlsx', 'psychomotor_domain')
    scores1 = []

    for i in range(len(clo1_verbs)):
        
        if word_list['1'].str.contains(clo1_verbs[i]).any():
            scores1.append(1)
        elif word_list['2'].str.contains(clo1_verbs[i]).any():
            scores1.append(2)
        elif word_list['3'].str.contains(clo1_verbs[i]).any():
            scores1.append(3)
        elif word_list['4'].str.contains(clo1_verbs[i]).any():
            scores1.append(4)
        elif word_list['5'].str.contains(clo1_verbs[i]).any():
            scores1.append(5)
        elif word_list['6'].str.contains(clo1_verbs[i]).any():
            scores1.append(6)
        else:
            scores1.append(0)
            
    scores2 = []

    for i in range(len(clo2_verbs)):
        if word_list['1'].str.contains(clo2_verbs[i]).any():
            scores2.append(1)
        elif word_list['2'].str.contains(clo2_verbs[i]).any():
            scores2.append(2)
        elif word_list['3'].str.contains(clo2_verbs[i]).any():
            scores2.append(3)
        elif word_list['4'].str.contains(clo2_verbs[i]).any():
            scores2.append(4)
        elif word_list['5'].str.contains(clo2_verbs[i]).any():
            scores2.append(5)
        elif word_list['6'].str.contains(clo2_verbs[i]).any():
            scores2.append(6)
        else:
            scores2.append(0)

    clo1_df = {'EKS':clo1, 'Verbs': clo1_verbs, 'Scores': scores1}
    clo1_df = pd.DataFrame(clo1_df)

    clo2_df = {'EKS':clo2, 'Verbs': clo2_verbs, 'Scores': scores2}
    clo2_df = pd.DataFrame(clo2_df)


    clo1_df['Dist'] = abs(clo1_df['Scores'][0] - clo1_df['Scores'])

    clo2_df['Dist'] = abs(clo2_df['Scores'][0] - clo2_df['Scores'])

    df2 = clo1_df[['EKS','Verbs','Dist']][1:]
    df3 = clo2_df[['EKS','Verbs','Dist']][1:]


    return df2, df3, clo1, clo2
    
    
#####################################33

#rule for affective domain

def rule_2_ad(page1):


    page1 = page1.replace('\n \n \n•','>>>').replace(')\n \n•', '>>>').replace('\n \n•', '>').replace('\n•','>').replace('\nEKS:', '')
    page1
    page1 = page1.split('>>>')
    del page1[0]
    i = 0
    for j in range(len(page1)):
        i += 1
        globals()["clo" + str(i)] = page1[j].split('>')

    sep = ' '
    clo1_verbs = []
    for i in range(len(clo1)):
        x = clo1[i].split(sep, 1)[0]
        clo1_verbs.append(x)
        
    clo2_verbs = []
    for i in range(len(clo2)):
        x = clo2[i].split(sep, 1)[0]
        clo2_verbs.append(x)

    word_list = pd.read_excel('word_list.xlsx', 'affective_domain')
    scores1 = []

    for i in range(len(clo1_verbs)):
        
        if word_list['1'].str.contains(clo1_verbs[i]).any():
            scores1.append(1)
        elif word_list['2'].str.contains(clo1_verbs[i]).any():
            scores1.append(2)
        elif word_list['3'].str.contains(clo1_verbs[i]).any():
            scores1.append(3)
        elif word_list['4'].str.contains(clo1_verbs[i]).any():
            scores1.append(4)
        elif word_list['5'].str.contains(clo1_verbs[i]).any():
            scores1.append(5)
        else:
            scores1.append(0)
            
    scores2 = []

    for i in range(len(clo2_verbs)):
        if word_list['1'].str.contains(clo2_verbs[i]).any():
            scores2.append(1)
        elif word_list['2'].str.contains(clo2_verbs[i]).any():
            scores2.append(2)
        elif word_list['3'].str.contains(clo2_verbs[i]).any():
            scores2.append(3)
        elif word_list['4'].str.contains(clo2_verbs[i]).any():
            scores2.append(4)
        elif word_list['5'].str.contains(clo2_verbs[i]).any():
            scores2.append(5)
        else:
            scores2.append(0)

    clo1_df = {'EKS':clo1, 'Verbs': clo1_verbs, 'Scores': scores1}
    clo1_df = pd.DataFrame(clo1_df)

    clo2_df = {'EKS':clo2, 'Verbs': clo2_verbs, 'Scores': scores2}
    clo2_df = pd.DataFrame(clo2_df)


    clo1_df['Dist'] = abs(clo1_df['Scores'][0] - clo1_df['Scores'])

    clo2_df['Dist'] = abs(clo2_df['Scores'][0] - clo2_df['Scores'])

    df2 = clo1_df[['EKS','Verbs','Dist']][1:]
    df3 = clo2_df[['EKS','Verbs','Dist']][1:]


    return df2, df3, clo1, clo2

