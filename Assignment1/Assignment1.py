
# coding: utf-8
from bs4 import BeautifulSoup
import requests
import csv
import re
import pandas as pd
pages = requests.get("https://www.reed.edu/catalog/people/faculty.html")
soup = BeautifulSoup(pages.content, 'html.parser')

#Separation of faculty members by <p> tag, but first 2 and last few are not faculty.
faculty = soup.find_all("p")

#Start from faculty[2] and end at faculty[169] for list of faculty

firstname = []
lastname = []
ugradschool = []
ugradyear = []
facultyschoolID = []
facultytitle = []
currentschool = []
currentdepartment = []

#Compiling regex since it will be reused for each person
regex_ugradschool = re.compile('PhD\s\d{4}\s(.*?)\.')
regex_ugradyear = re.compile('PhD\s(.*?)\s')
regex_facultytitle = re.compile('><br/>\n(.*?)<br/>')
regex_udegree = re.compile('PhD')
regex_firstname = re.compile('(.*?)\s')
regex_lastname = re.compile('\s.*')
regex_currentdepartment = re.compile('(?<=of\s).*')
school_ID = 370

for i in range(2,169):
    #Check if PhD exists. We only want professors with PhD's
    if regex_udegree.search(str(faculty[i]).strip()) is not None:
        #Means that the professor has a PhD
        firstname.append(regex_firstname.findall(faculty[i].strong.get_text())[0].strip())
        lastname.append(regex_lastname.findall(faculty[i].strong.get_text())[0].strip())
        ugradschool.append(regex_ugradschool.findall(str(faculty[i]))[0].strip())
        ugradyear.append(regex_ugradyear.findall(str(faculty[i]))[0].strip())
        facultyschoolID.append(school_ID)
        currentschool.append('Reed College')
        #Convert title to either Professor, Assistant Professor, Scholar, or Associate Professor
        #Scholar is only unique title, its department is Sociology.
        title = regex_facultytitle.findall(str(faculty[i]))[0].strip()
        if 'Scholar' in title:
            currentdepartment.append('Sociology')
            facultytitle.append('Scholar')
        elif 'Associate Professor' in title:
            facultytitle.append('Associate Professor')
            currentdepartment.append(regex_currentdepartment.findall(title)[0])
        elif 'Assistant Professor' in title:
            facultytitle.append('Assistant Professor')
            currentdepartment.append(regex_currentdepartment.findall(title)[0])
        else:
            facultytitle.append('Professor')
            currentdepartment.append(regex_currentdepartment.findall(title)[0])

#Creating dataframe. Adding extra columns that weren't previously made, and filling them with nothing.
data = pd.DataFrame({'First Name': firstname, 'Lastname': lastname, 'university of PhD': ugradschool, 'year of PhD': ugradyear, 'current university': currentschool, 'current university ID': facultyschoolID, 'department of current faculty': currentdepartment, 'job title': facultytitle})
new_index = ['First Name', 'Lastname', 'university of PhD', 'university of PhD ID', 'department of PhD', 'year of PhD', 'current university', 'current university ID', 'department of current faculty', 'year faculty started', 'job title']
data = data.reindex(columns=new_index, fill_value='')


#This connects the PhD school to the ID, and if it doesn't exist, create them. Added already to spreadsheet.
phdID = []
codename = []
codeID = []
count = 402
missingschools = dict()
codereader = csv.DictReader(open('Assignment1_school_codes.csv'))
for row in codereader:
    codeID.append(row['id'])
    codename.append(row['name'])
codeDict = dict(zip(codename, codeID))

reedreader = csv.DictReader(open('assignment1-reedcollege.csv'))
for row in reedreader:
    uni = row['university of PhD']
    if 'University of California' in uni:
        uccheck = uni.replace('University of California,', 'UC')
        phdID.append(codeDict[uccheck])
    elif uni in codeDict:
        phdID.append(codeDict[uni])
    #If university is not in the dictionary, double check for edge cases first
    elif uni not in codeDict:
        if 'University of Cambridge' in uni:
            phdID.append(codeDict['Cambridge University'])
        elif 'University of Oregon' in uni:
            phdID.append(codeDict['University of Oregon, Eugene'])
        elif 'University of Pennsylvania' in uni:
            phdID.append(codeDict['University of Pennsylvania Club'])
        elif 'University of Maryland' in uni:
            phdID.append('')
        elif 'University of Michigan' in uni:
            phdID.append('')
        elif 'Colorado State University' in uni:
            phdID.append(codeDict['Colorado State University, Fort Collins'])
        elif 'Indiana University' in uni:
            phdID.append('')
        elif 'University of Wisconsin' in uni:
            phdID.append('')
        elif 'University of New Hampshire' in uni:
            phdID.append(codeDict['University of New Hampshire, Durham'])
        #Edge cases covered. All the rest are schools that currently do not exist in the school codes. Giving them unique codes, starting from 402
        else:
            missingschools[uni] = count
            phdID.append(str(count))
            count = count + 1

data['university of PhD ID'] = phdID

data.to_csv('assignment1-reedcollege.csv')
print('Data converted to assignment1-reedcollege.csv')
