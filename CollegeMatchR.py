# -*- coding: utf-8 -*-
import requests, time, json
from bs4 import BeautifulSoup


def all_states():
    r = requests.get('https://alphabetizer.flap.tv/lists/list-of-states-in-alphabetical-order.php')
    states_search = BeautifulSoup(r.text, 'html.parser')
    state_finder = states_search.find('ul')

    states = []
    for state in state_finder.find_all('li'):
        states.append(state.text)
    return states

states = all_states()

def college_selection(states):
    selected_state = input("Welcome to CollegeMatchR%s, where we help you find the college that's right for you!\nLets get started! Which state are you interested in?(First letter must be capitalized for each name) "%(u'\u2122'))

    while selected_state not in states:
        selected_state = input("Whoops! We couldn't find what you're looking for. Lets try again!\nWhich state are you interested in?(First letter must be capitalized for each name) ")

    if " " in selected_state:
        selected_state = selected_state.replace(" ", "-")

    rankings_by_state = requests.get('https://www.niche.com/colleges/search/best-colleges/s/{}'.format(selected_state))
    parse_school_data = BeautifulSoup(rankings_by_state.text, 'html.parser')
    lst_of_school = parse_school_data.find('ol')

    lst =[]
    universities_info1 = {}
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
            universities_info1[schools]={'Location':location,'School Type':school_type,'Acceptance Rates':acceptance_rates,'Test Scores':test_scores}
        except :
            pass
    return universities_info1,lst

universities,lst = college_selection(states)


def more_data(universities, lst):
    global school_rank
    modified_school_name = ''
    for school in lst:
        if ' ' in school:
            modified_school_name = (school.replace(' - ', '-').replace(' of ', '-').replace(' ', '-').replace('&',''))

        s = requests.get(r'https://www.timeshighereducation.com/world-university-rankings/{}'.format(modified_school_name))
        rankings_finder = BeautifulSoup(s.text, 'html.parser')

        try:
            school_rank = rankings_finder.find('div', attrs={'class': 'rank col-xs-6'}).div.span.text.replace('> ','').replace('=','')
            content_placeholder = rankings_finder.find("div", attrs={'class': 'panel-pane pane-data-stats'}).div.ul.find_all('li')

            universities[school].update({'School Rank': school_rank})
            for info in content_placeholder:
                if 'Number of Students' in info.text:
                    student_size = info.text
                    student_size = student_size.replace('Number of Students', '')
                    universities[school].update({'Student Size': student_size})


                if 'No. of students per staff' in info.text:
                    students_per_staff = info.text
                    students_per_staff = students_per_staff.replace('No. of students per staff', '')
                    universities[school].update({'Students Per Staff': students_per_staff})



                if 'Percentage of International Students' in info.text:
                    international_student_percentage = info.text
                    international_student_percentage = international_student_percentage.replace('Percentage of International Students', '')
                    universities[school].update({'Internationl Student Percentage': international_student_percentage})



                if 'Student Ratio of Females to Males' in info.text:
                    male_to_female_ratio = info.text
                    male_to_female_ratio = male_to_female_ratio.replace('Student Ratio of Females to Males', '')
                    universities[school].update({'Male to Female Ratio': male_to_female_ratio})



                if 'Out-of-state Tuition and Fees' in info.text:
                    out_of_state_tution = info.text
                    out_of_state_tution = out_of_state_tution.replace('Out-of-state Tuition and Fees', '')
                    universities[school].update({'Out of State Tution': out_of_state_tution})



                if 'On-campus Room and Board' in info.text:
                    on_campus_tution = info.text
                    on_campus_tution = on_campus_tution.replace('On-campus Room and Board', '')
                    universities[school].update({'In-State Tution': on_campus_tution})



                if 'Salary after 10 years' in info.text:
                    salary_post_ten_years = info.text
                    salary_post_ten_years = salary_post_ten_years.replace('Salary after 10 years', '')
                    universities[school].update({'Salary After 10 Years': salary_post_ten_years})



        except:
            universities[school].update({'School Rank': 'N/A'})
            pass

print("Hang tight! We're working on it!")
for i in range(1, 101, 1):
    print("\r{0}%".format(i), end="")
    time.sleep(.35)
print('\\n'+json.dumps(universities, indent=4))

more_data(universities, lst)



