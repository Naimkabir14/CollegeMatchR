# -*- coding: utf-8 -*-
import dict2xml
import requests, json
from bs4 import BeautifulSoup
from tinydb import TinyDB, Query

db = TinyDB('db.json')

def all_states():
    r = requests.get('https://alphabetizer.flap.tv/lists/list-of-states-in-alphabetical-order.php')
    states_search = BeautifulSoup(r.text, 'html.parser')
    state_finder = states_search.find('ul')

    states = []
    for state in state_finder.find_all('li'):
        states.append(state.text)
    return states

universities = {}
states = all_states()
def college_selection(state):

    rankings_by_state = requests.get('https://www.niche.com/colleges/search/best-colleges/s/{}'.format(state.replace(" ", "-")))# Dynamically searches through Niche.com
    parse_school_data = BeautifulSoup(rankings_by_state.text, 'html.parser')# Parses Html Data
    lst_of_school = parse_school_data.find('ol')

    lst =[]
    for item in lst_of_school.findAll('li'):
        try:
            schools = (item.find('h2').text)

            school_type = item.ul.li.text

            location = item.ul.li.find_next_sibling().text

            base_element = item.ul.find_next_sibling(attrs={'class': 'search-result-fact-list'}).li.find_next_sibling()
            rates = base_element.text

            acceptance_rates = rates.split('%', 1)[0]+'%'

            test_scores = base_element.find_next_sibling().find_next_sibling().div.span.text

            if '—' in test_scores:
                test_scores = 'N/A'
            if '—' in acceptance_rates:
                acceptance_rates = 'N/A'
            if '—' in school_type:
                school_type = 'N/A'

            lst.append(schools)
            universities.setdefault(state, [])
            universities[state].append({schools:[{'Location':location,'School Type':school_type,'Acceptance Rates':acceptance_rates,'SAT Score Range':test_scores}]})

        except Exception:
            pass

    return universities,lst

for state in states:
    universities,lst = college_selection(state)

    def more_data(universities, lst, state):
        global school_rank
        modified_school_name = ''
        count = 0
        for school in lst:
            if ' ' in school:
                modified_school_name = (school.replace(' - ', '-').replace(' of ', '-').replace(' ', '-').replace('&',''))
                
            s = requests.get(r'https://www.timeshighereducation.com/world-university-rankings/{}'.format(modified_school_name))
            rankings_finder = BeautifulSoup(s.text, 'html.parser')

            try:
                school_rank = rankings_finder.find('div', attrs={'class': 'rank col-xs-6'}).div.span.text.replace('> ','').replace('=','')
                content_placeholder = rankings_finder.find("div", attrs={'class': 'panel-pane pane-data-stats'}).div.ul.find_all('li')

                if school_rank == str(800):
                    school_rank = school_rank+'+'
                    
                universities[state][count][school][0].update({'School Rank': school_rank})

                for info in content_placeholder:
                    if 'Number of Students' in info.text:
                        student_size = info.text
                        student_size = student_size.replace('Number of Students', '')
                        universities[state][count][school][0].update({'Student Size': student_size})
                        
                    if 'No. of students per staff' in info.text:
                        students_per_staff = info.text
                        students_per_staff = students_per_staff.replace('No. of students per staff', '')
                        universities[state][count][school][0].update({'Students Per Staff': students_per_staff})
                        
                    if 'Percentage of International Students' in info.text:
                        international_student_percentage = info.text
                        international_student_percentage = international_student_percentage.replace('Percentage of International Students', '')
                        universities[state][count][school][0].update({'International Student Percentage': international_student_percentage})

                    if 'Student Ratio of Females to Males' in info.text:
                        male_to_female_ratio = info.text
                        male_to_female_ratio = male_to_female_ratio.replace('Student Ratio of Females to Males', '')
                        universities[state][count][school][0].update({'Male to Female Ratio': male_to_female_ratio})
                        
                    if 'Out-of-state Tuition and Fees' in info.text:
                        out_of_state_tuition = info.text
                        out_of_state_tuition = out_of_state_tuition.replace('Out-of-state Tuition and Fees', '')
                        universities[state][count][school][0].update({'Out of State Tuition': out_of_state_tuition})
                        
                    if 'On-campus Room and Board' in info.text:
                        on_campus_tuition = info.text
                        on_campus_tuition = on_campus_tuition.replace('On-campus Room and Board', '')
                        universities[state][count][school][0].update({'In-State Tuition': on_campus_tuition})

                    if 'Salary after 10 years' in info.text:
                        salary_post_ten_years = info.text
                        salary_post_ten_years = salary_post_ten_years.replace('Salary after 10 years', '')
                        universities[state][count][school][0].update({'Salary After 10 Years': salary_post_ten_years})

            except:
                pass

            count = count + 1


    more_data(universities, lst, state)

db.insert(universities)# Stores Dictionary into database
db.all()
find_school = Query() # Object Query is used search for data
db.search(find_school.Alabama == 'University Of Alabama')

with open('data.json', 'w') as outfile:
    json.dump(universities, outfile, indent=4)


xml = dict2xml.dict2xml(universities, 'Universities')
with open('xm.xml', 'a') as outfile:
        outfile.write(xml)
