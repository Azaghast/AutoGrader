import streamlit as st
import numpy as np
from summarizer import Summarizer
from transformers import *
import preshed
import cymem
import FileFunctions

@st.cache(hash_funcs={preshed.maps.PreshMap:lambda _:None,cymem.cymem.Pool:id},suppress_st_warning=True,allow_output_mutation=True)
def init_scibert():
    scibert_config = AutoConfig.from_pretrained('allenai/scibert_scivocab_uncased')
    scibert_config.output_hidden_states=True
    scibert_tokenizer = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
    scibert = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased',config=scibert_config)
    model = Summarizer(custom_model=scibert,custom_tokenizer=scibert_tokenizer)
    return model

def summarize_answers(summarizer,answers):
    summarized_ans_list = []
    for answer in answers:
        ans_split = split_into_sentences(answer)
        summ = summarizer(answer,ratio=(5/len(ans_split)))
        summarized_ans_list.append(summ)
    return summarized_ans_list

st.title("AutoGrader Teacher Portal")

st.write("Please wait until the model has finished loading...")
scibert = init_scibert()
st.write("Model has finished loading!")

st.set_option('deprecation.showfileUploaderEncoding', False)

teacher_file = st.file_uploader(label="Upload teacher's file",type='txt',encoding='utf-8',key='key1')
teacher_submit = st.button(label="Submit teacher's file",key='bkey1')    
if teacher_submit:
    text = teacher_file.getvalue().lower()
    teacher_details, teacher_questions, teacher_answers= FileFunctions.get_questions_answers('teacher',text)
    summ_ans_list = summarize_answers(scibert,teacher_answers)
    filename = teacher_details[0]+'temp_file_name.txt'
    flag = FileFunctions.make_final_file(filename,teacher_questions,summ_ans_list)
    if flag:
        processed_text = open('C:\\Users\\Azaghast\\AutoGrader\\Processed Answer Files\\'+filename,'r',encoding='utf-8').read()
        link = FileFunctions.download_link(processed_text,'teacher_downloaded_file.txt','Click to download summarized answers textfile')
        st.markdown(link, unsafe_allow_html=True)
    else:
        st.write('Check original input file and try again')
    