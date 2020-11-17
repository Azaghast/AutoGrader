import wikipedia as wk
import csv
import pickle

def get_main_hyperlinks():
    return wk.page("Outline of machine learning").links

def parse_page(title):
    page = wk.WikipediaPage(title=title)
    return page.content

def preprocess_parsed_text(title):
    content_str = parse_page(title)
    content_split = content_str.split('\n')

    ctr = 0
    content_dict = {}
    key_list = []

    while(ctr<len(content_split)):
        print('going on...\n')
        curr_str = content_split[ctr]
        if (len(curr_str)!=0):
            if "==" in curr_str:
                flag = False
                ctr2 = ctr+1
                test_list = []
                while(flag==False and ctr2<len(content_split)):
                    next_str = content_split[ctr2]
                    if len(next_str)!=0:
                        if "==" in next_str:
                            flag = True
                        else:
                            test_list.append(next_str)
                            ctr2+=1
                    else:
                        ctr2+=1
                key = curr_str.replace('=','').strip()
                key_list.append(key)
                content_dict[key]=test_list
                ctr=ctr2
            else:
                ctr+=1
        else:
            content_split.pop(ctr)
    
    return key_list,content_dict

hyperlinks = get_main_hyperlinks()

hyperlink_dump = open('wikipedia_titles','wb')
pickle.dump(hyperlinks,hyperlink_dump)
hyperlink_dump.close()

parsed_text_dict = {}

print('creating the parsed text dictionary...')
for i in range(len(hyperlinks)):
    try:
        curr_title = hyperlinks[i]
        key_list,content_dict = preprocess_parsed_text(curr_title)
        parsed_text_dict[curr_title] = (key_list,content_dict)
    except wk.exceptions.PageError:
        continue
print('done creating the parsed text dictionary')


parsed_text_dump = open('parsedtext','wb')
pickle.dump(parsed_text_dict,parsed_text_dump)
parsed_text_dump.close()
print('done pickling the parsed text dictionary')