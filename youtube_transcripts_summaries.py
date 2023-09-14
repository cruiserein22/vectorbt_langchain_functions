from langchain import PromptTemplate, LLMChain
from langchain.document_loaders import YoutubeLoader
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import find_dotenv, load_dotenv
import tiktoken
import os
import streamlit as st
import time


openai_api_key = os.getenv("OPENAI_API_KEY")

#load YT url

def load_yt(url):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", openai_api_key=openai_api_key)
    loader = YoutubeLoader.from_youtube_url(url, add_video_info=True)
    result = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=0)
    texts = text_splitter.split_documents(result)

    chain = load_summarize_chain(llm, chain_type="map_reduce", verbose=True)
    ran_chain = chain.run(texts)
    return ran_chain


def main():
    load_dotenv(find_dotenv())

    st.set_page_config(page_title="Youtube Summarizer")
    st.header("Youtube Summarizer")
    url = st.text_input("Enter the Youtube URL of the Video You Want to Summarize")
    
   
    if url:
            
            st.write("Summarizing this video: ", url)
            
            with st.spinner('Transcribing video'):
                time.sleep(15)
            #functions
            transcript = load_yt(url)
            with st.spinner('Summarizing video'):
                time.sleep(10)
            # bullets = generate_bullets(transcript)
            
           
            # st.success('Done!')
        
            with st.expander("Summary"):
                st.write(transcript)



if __name__ == '__main__':
    main()