import streamlit as st
import pytrends
from pytrends.request import TrendReq
import pandas as pd
import numpy as np
import requests
from GoogleNews import GoogleNews

st.set_page_config(layout="wide")

# build request parameters
timeframe = "now 7-d"

kw = st.sidebar.text_input('Enter a Keyword', None, type = 'default')
kw_list = [kw]

number_of_related_queries = st.sidebar.slider('# of Related Queries', min_value=0, max_value=4, value=2)

get_data_button = st.sidebar.button('Get Google Trends Data')

if get_data_button:
  pytrends = TrendReq()
  pytrends.build_payload(kw_list, cat=0, timeframe = timeframe, geo = 'US')

  #get top related queries for provided keyword
  related_queries = pytrends.related_queries()
  related_queries.values()

  #build kw list that includes provided and related top queries
  top_df = list(related_queries.values())[0]['top'].head(number_of_related_queries)
  top_related_list = top_df['query'].tolist()
  kw_list.extend(top_related_list)

  #get interest over time
  pytrends.build_payload(kw_list, cat=0, timeframe = timeframe, geo = 'US')
  interest_o_time_df = pytrends.interest_over_time()
  interest_o_time_df = interest_o_time_df.drop(columns=['isPartial'])

  st.line_chart(data=interest_o_time_df)
  
  #get rising queries
  rising_df = list(related_queries.values())[0]['rising']
  st.dataframe(data=rising_df)
