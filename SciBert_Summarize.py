from summarizer import Summarizer
from transformers import *

scibert_config = AutoConfig.from_pretrained('allenai/scibert_scivocab_uncased')
scibert_config.output_hidden_states=True
scibert_tokenizer = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
scibert = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased',config=scibert_config)
model = Summarizer(custom_model=scibert,custom_tokenizer=scibert_tokenizer)
    
def summarize(context,num_sentences):
    summary = model(context.lower(),num_sentences)
    return summary
    
'''if __name__ == '__main__':
    text = 'hi hello'
    summ = summarize(text,1)
    print(summ)'''