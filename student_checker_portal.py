import streamlit as st
from transformers import AutoTokenizer
import math
import numpy as np
import nltk
from nltk.corpus import stopwords
import FileFunctions
from SplitIntoSentences import split_into_sentences
import sklearn 

st.set_option('deprecation.showfileUploaderEncoding', False)

@st.cache()
def init_pegasus_tokenizer():
    tokenizer = AutoTokenizer.from_pretrained('google/pegasus-large')
    return tokenizer

@st.cache(persist=True)
def get_stopwords():
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))
    return stop_words

def remove_stopwords(text_split,stop_words):
    text_no_stop = []
    for i in range(len(text_split)):
        result = ''
        for j in text_split[i].split(' '):
            if len(j)>0 and j not in stop_words:
                result+=(j+' ')
        text_no_stop.append(result.rstrip())
    return text_no_stop

def get_similarity_scores(context_split_no_stopwords,ans_split_no_stopwords,tokenizer):
    res_list = []
    for i in range(len(ans_split_no_stopwords)):
        temp1 = tokenizer(ans_split_no_stopwords[i].strip())['input_ids']
        temp1 = np.asarray(temp1,dtype=np.float32)
        temp1_scores = []
        for j in range(len(context_split_no_stopwords)):
            temp2 = tokenizer(context_split_no_stopwords[j].strip())['input_ids']
            temp2 = np.asarray(temp2,dtype=np.float32)
            temp1_len = len(temp1)
            temp2_len = len(temp2)
            if temp2_len>=temp1_len:
                temp1_pad = np.pad(temp1,((temp2_len-temp1_len),0),'constant')
                dp = np.dot(temp1_pad,temp2)
                norm_temp1 = np.linalg.norm(temp1_pad)
                norm_temp2 = np.linalg.norm(temp2)
                cos = dp/(norm_temp1*norm_temp2)
                temp1_scores.append(cos)
            elif temp1_len>temp2_len:
                temp2_pad = np.pad(temp2,((temp1_len-temp2_len),0),'constant')
                dp = np.dot(temp1,temp2_pad)
                norm_temp1 = np.linalg.norm(temp1)
                norm_temp2 = np.linalg.norm(temp2_pad)
                cos = dp/(norm_temp1*norm_temp2)
                temp1_scores.append(cos)
        res_list.append(temp1_scores)
    st.dataframe(res_list)
    return res_list    

def check_unique(scores_list,answer_list):
    unique_checker = []
    for i in range(len(answer_list)):
        unique_checker.append(scores_list[i].index(max(scores_list[i])))
    corrences_dict = {}
    for i in range(len(unique_checker)):
        corrence = []
        for j in range(len(unique_checker)):
            if i!=j:
                if unique_checker[i]==unique_checker[j]:
                    corrence.append(j)
        corrences_dict[i]=corrence
    return unique_checker, corrences_dict

def grade_answer(max_marks,context,answer,score_list,corrences_dict,unique_checker):
    true_num_points = len(context)
    marks_per_point = max_marks/true_num_points
    ans_num_points = len(answer)
    ans_marks = 0
    not_unique = []
    for i in range(ans_num_points):
        if i not in not_unique:
            ref = corrences_dict[i]
            if len(ref)>0:
                ans_marks+=marks_per_point
                for j in ref:
                    if j not in not_unique:
                        not_unique.append(j)
            else:
                curr_point_score = score_list[i][unique_checker[i]]
                if curr_point_score>=0.8:
                    ans_marks+=marks_per_point
                elif curr_point_score<0.8 and curr_point_score>=0.6:
                    ans_marks+=(marks_per_point*(4/5))
                elif curr_point_score<0.6 and curr_point_score>=0.4:
                    ans_marks+=(marks_per_point*(3/5))
                elif curr_point_score<0.4 and curr_point_score>=0.2:
                    ans_marks+=(marks_per_point*(2/5))
                elif curr_point_score<0.2 and curr_point_score>=0.1:
                    ans_marks+=(marks_per_point*(1/5))
                else:
                    ans_marks+=0
    st.write('marks in fp:',ans_marks)
    ans_checker = ans_marks - math.floor(ans_marks)
    if ans_checker>=0.65:
        ans_marks = math.ceil(ans_marks)
    elif ans_checker<=0.35:
        ans_marks = math.floor(ans_marks)
    else:
        ans_marks = (math.ceil(ans_marks)+math.floor(ans_marks))/2
    return ans_marks

st.title('AutoGrader Student Answer Grader Portal')
st.write("Please wait until the model has finished loading...")
pegasus_tokenizer = init_pegasus_tokenizer()
st.write("Model has finished loading!")

teacher_file = st.file_uploader(label="Upload teacher's file",type='txt',encoding='utf-8',key='teacher_file')

student_file = st.file_uploader(label="Upload student's file",type='txt',encoding='utf-8',key='student_file')
student_submit = st.button(label="Submit student's file",key='student_submit_button')

if teacher_file!=None and student_file!=None and student_submit:
    teacher_doc_text = teacher_file.getvalue().lower()
    teacher_details, teacher_questions, teacher_answers = FileFunctions.get_questions_answers('teacher',teacher_doc_text)
    student_doc_text = student_file.getvalue().lower()
    if len(student_doc_text)>0:
        student_details, student_questions, student_answers = FileFunctions.get_questions_answers('student',student_doc_text)

        if len(teacher_questions)==len(student_questions) and len(teacher_answers)==len(student_answers):
            stopwords = get_stopwords()
            grades = []
            for i in range(len(student_answers)):
                curr_context = teacher_answers[i]
                curr_student_ans = student_answers[i]
                context_split = split_into_sentences(curr_context)
                ans_split = split_into_sentences(curr_student_ans)
                context_split_no_stopwords = remove_stopwords(context_split,stopwords)
                ans_split_no_stopwords = remove_stopwords(ans_split,stopwords)
                scores_list = get_similarity_scores(context_split_no_stopwords,ans_split_no_stopwords,pegasus_tokenizer)
                unique_list, coccurrence_dict = check_unique(scores_list,ans_split_no_stopwords)
                st.write(coccurrence_dict)
                marks = grade_answer(5,context_split,ans_split,scores_list,coccurrence_dict,unique_list)
                st.write("Question #",i+1,"scored",marks,'marks')
                grades.append(marks)
            flag = FileFunctions.generate_report(student_details,grades)
            if flag:
                filename = student_details[0]+student_details[1]+student_details[4]+'.txt'
                report_to_download = open('C:\\Users\\Azaghast\\AutoGrader\\Report\\'+filename,'r',encoding='utf-8').read()
                link = FileFunctions.download_link(report_to_download,'student_report_download.txt','Click to download the student report textfile')
                st.markdown(link, unsafe_allow_html=True)
            else:
                st.write('There was some error in creating report')
