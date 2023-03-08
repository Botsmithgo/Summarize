import os
from time import time, sleep
import textwrap
import openai
import re
import streamlit as st

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

openai.api_key = open_file('openaiapikey.txt')

def save_file(content, filepath):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

@st.cache
def gpt3_completion(prompt, engine='text-davinci-003', temp=0.5, top_p=1.0, tokens=2000, freq_pen=0.25, pres_pen=0.0, stop=['<<END>>']):
    max_retry = 5
    retry = 0
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            text = re.sub('\s+', ' ', text)
            # Remove prompt from summary
            text = re.sub(r'^.*?RESPONSE:\n\n', '', text, flags=re.DOTALL)
            filename = '%s_gpt3.txt' % time()
            with open('gpt3_logs/%s' % filename, 'w') as outfile:
                outfile.write('PROMPT:\n\n' + prompt + '\n\n==========\n\nRESPONSE:\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)

def main():
    st.title('GPT-3 Summarizer')

    # Add a file uploader element to the GUI
    uploaded_file = st.file_uploader('Upload a text file to summarize')

    if uploaded_file is not None:
        file_contents = uploaded_file.read().decode('utf-8')
        chunks = textwrap.wrap(file_contents, width=3000)
        summary_prompt = open_file('prompt.txt')

        result = ''
        for count, chunk in enumerate(chunks, 1):
            prompt = summary_prompt.replace('<<SUMMARY>>', chunk)
            prompt = prompt.encode(encoding='ASCII', errors='ignore').decode()
            st.write(f'Summarizing chunk {count} of {len(chunks)}...')
            summary = gpt3_completion(prompt)
            
            
            result += summary + '\n\n'
            
        st.write('All summaries:')
        st.write(result)

        # Remove prompts from the result string
        result = re.sub(r'PROMPT:.*?RESPONSE:\n\n', '', result, flags=re.DOTALL)

        # Save the result to a file
        filename = f'output_{time()}.txt'
        save_file(result, filename)
        st.success(f'Summary saved to {filename}.')

# Add a Streamlit app decorator to run the program
if __name__ == '__main__':
    main()