import streamlit as st
import pytrends
from pytrends.request import TrendReq
import pandas as pd
import numpy as np
import requests
from GoogleNews import GoogleNews

kw = st.text_input('Enter a Keyword', None, type="default")
kw_list = [kw]

# build request parameters
timeframe = "now 7-d"
number_of_related_queries = 3

if kw is not None:
  pytrend = TrendReq()
  pytrend.build_payload(kw_list, cat=0, timeframe = timeframe, geo = 'US')

  #get top related queries for provided keyword
  related_queries = pytrend.related_queries()
  related_queries.values()

  #build kw list that includes provided and related top queries
  top_df = list(related_queries.values())[0]['top'].head(number_of_related_queries)
  top_related_list = top_df['query'].tolist()
  kw_list.append(top_related_list)

  #get interest over time
  pytrend.build_payload(kw_list, cat=0, timeframe = timeframe, geo = 'US')
  interest_o_time_df = pytrend.interest_over_time()
  interest_o_time_df = interest_o_time_df.drop(columns=['isPartial'])

  st.line_chart(data=interest_o_time_df)
