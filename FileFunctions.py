import re
import base64

def get_questions_answers(mode,text):
    questions_list = []
    answers_list = []
    subject_name = []
    person_details = []

    if mode=='student':
        name_start_tag = '<name>'
        name_end_tag = '</name>'
        roll_start_tag = '<roll>'
        roll_end_tag = '</roll>'
        degree_start_tag = '<degree>'
        degree_end_tag = '</degree>'
        sem_start_tag = '<semester>'
        sem_end_tag = '</semester>'

        name_start_end_pos = [m.end() for m in re.finditer(name_start_tag,text)]
        name_end_start_pos = [m.start() for m in re.finditer(name_end_tag,text)]
        roll_start_end_pos = [m.end() for m in re.finditer(roll_start_tag,text)]
        roll_end_start_pos = [m.start() for m in re.finditer(roll_end_tag,text)]
        degree_start_end_pos = [m.end() for m in re.finditer(degree_start_tag,text)]
        degree_end_start_pos = [m.start() for m in re.finditer(degree_end_tag,text)]
        sem_start_end_pos = [m.end() for m in re.finditer(sem_start_tag,text)]
        sem_end_start_pos = [m.start() for m in re.finditer(sem_end_tag,text)]

        name = text[name_start_end_pos[0]:name_end_start_pos[0]]
        roll_no = text[roll_start_end_pos[0]:roll_end_start_pos[0]]
        degree = text[degree_start_end_pos[0]:degree_end_start_pos[0]]
        sem = text[sem_start_end_pos[0]:sem_end_start_pos[0]]
        
        person_details.append(name)
        person_details.append(roll_no)
        person_details.append(degree)
        person_details.append(sem)

    elif mode=='teacher':
        prof_start_tag = '<professor>'
        prof_end_tag = '</professor>'

        prof_start_end_pos = [m.end() for m in re.finditer(prof_start_tag,text)]
        prof_end_start_pos = [m.start() for m in re.finditer(prof_end_tag,text)]

        prof = text[prof_start_end_pos[0]:prof_end_start_pos[0]]
        person_details.append(prof)

    question_start_tag = '<question>'
    question_end_tag = '</question>'
    answer_start_tag = '<answer>'
    answer_end_tag = '</answer>'
    subject_start_tag = '<subject>'
    subject_end_tag = '</subject>'

    question_start_end_pos = [m.end() for m in re.finditer(question_start_tag,text)]
    question_end_start_pos = [m.start() for m in re.finditer(question_end_tag,text)]
    answer_start_end_pos = [m.end() for m in re.finditer(answer_start_tag,text)]
    answer_end_start_pos = [m.start() for m in re.finditer(answer_end_tag,text)]
    subject_start_end_pos = [m.end() for m in re.finditer(subject_start_tag,text)]
    subject_end_start_pos = [m.start() for m in re.finditer(subject_end_tag,text)]

    person_details.append(text[subject_start_end_pos[0]:subject_end_start_pos[0]])

    for i in range(len(question_start_end_pos)):
        questions_list.append(text[question_start_end_pos[i]:question_end_start_pos[i]])
        answers_list.append(text[answer_start_end_pos[i]:answer_end_start_pos[i]])        
    
    #person details has: name, roll_no, degree, sem, subject at indices 0,1,2,3,4 respectively

    return person_details, questions_list, answers_list

def make_final_file(teacher_details,questions,answers):
    question_start_tag = '<question>'
    question_end_tag = '</question>\n'
    answer_start_tag = '<answer>'
    answer_end_tag = '</answer>\n'
    final_file = open('C:\\Users\\Azaghast\\AutoGrader\\Processed Answer Files\\'+name,'w',encoding='utf-8')
    final_file.write('Name:'+teacher_details[0]+'\n')
    if (len(questions)==len(answers)):
        for i in range(len(questions)):
            question = question_start_tag+(questions[i].replace('\n',' ').strip())+question_end_tag
            answer = answer_start_tag+(answers[i].replace('\n',' ').strip())+answer_end_tag
            final_file.write(question+'\n')
            final_file.write(answer+'\n')
        return True
    else:
        return False
        
def download_link(object_to_download,download_filename,download_link_text):
    b64 = base64.b64encode(object_to_download.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

def generate_report(student_details,marks_list):
    name = student_details[0]
    roll = student_details[1]
    degree = student_details[2]
    sem = student_details[3]
    subject = student_details[4]
    filename = name+roll+subject+'.txt'
    file = open('C:\\Users\\Azaghast\\AutoGrader\\Report\\'+filename,'w',encoding='utf-8')
    file.write('Class:'+degree+' '+subject+'\n')
    file.write('Paper:'+subject+'\n')
    total = 0
    for i in range(len(marks_list)):
        text = 'Question #'+str(i+1)+' Marks:'+str(marks_list[i])+'\n'
        file.write(text)
        total+=marks_list[i]
    file.write('\nTotal:'+str(total))
    return True

