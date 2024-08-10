import os
import json
import pandas as pd
import traceback
from dotenv import load_dotenv
import PyPDF2

from src.logger import logging
from src.utils import read_file,get_tabke_data

from langchain.chat_models import ChatOpenAI
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.callbacks import get_openai_callback

load_dotenv()
key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(openai_api_key = key,
                 model_name = "gpt-3.5-turbo", 
                 temperature = 0.7)

TEMPLATE = """ 
Text:{text}
You are an expert MCQ maker. Given the above text, \
create a quiz of {number} multiple choice questions for {subject} students in {tone} difficulty. 
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your response like  RESPONSE_JSON below  and use it as a guide. \
Ensure to make {number} MCQs
{response_json}
"""

quiz_generation_prompt = PromptTemplate(
    input_variables=["text","number","subject","tone",'response_json'],
    template=TEMPLATE
)
quiz_chain = LLMChain(llm = llm, 
                      prompt = quiz_generation_prompt,
                      output_key = 'quiz',
                      verbose = True)

TEMPLATE2="""
You are an expert english grammarian and writer. Given a Multiple Choice Quiz for {subject} students.\
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity analysis. 
if the quiz is not at per with the cognitive and analytical abilities of the students,\
update the quiz questions which needs to be changed and change the difficulty such that it perfectly fits the student abilities
Quiz_MCQs:
{quiz}

Check from an expert English Writer of the above quiz:
"""

quiz_evaluation_prompt = PromptTemplate(input_variables=["subject","quiz"], template=TEMPLATE2)
review_chain = LLMChain(llm = llm,
                        prompt = quiz_evaluation_prompt,
                        output_key = 'review',
                        verbose = True)
generate_evaluate_chain=SequentialChain(chains=[quiz_chain, review_chain], 
                                        input_variables=["text", "number", "subject", "tone", "response_json"],
                                        output_variables=["quiz", "review"], verbose=True,)