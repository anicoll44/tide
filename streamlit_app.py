import streamlit as st
import pytrends
from pytrends.request import TrendReq
import pandas as pd
import numpy as np
import requests
from GoogleNews import GoogleNews

#Set width of page to fullscreen
st.set_page_config(layout="wide")

#Build sidebar and set request paramaeters
timeframe = "now 7-d"

kw = st.sidebar.text_input('Enter a Target Keyword', '', type = 'default')
kw_list = [kw]

timeframe = st.sidebar.selectbox(
     'Timeframe',
     ("Past 1 Hour", "Past 4 Hours", "Past 24 Hours", "Past 7 Days", "Past 30 Days", "Past 90 Days", "Past 12 Months", "Past 5 Years"), index = 3)

if timeframe == "Past 7 Days":
  timeframe = "now 7-d"
elif timeframe == 'Past 1 Hour':
  timeframe = 'now 1-H'
elif timeframe == 'Past 4 Hours':
  timeframe = 'now 4-H'
elif timeframe == 'Past 24 Hours':
  timeframe = 'now 1-d'
elif timeframe == 'Past 30 Days':
  timeframe = 'today 1-m'
elif timeframe == 'Past 90 Days':
  timeframe = 'today 3-m'
elif timeframe == 'Past 12 Months':
  timeframe = 'today 12-m'
elif timeframe == 'Past 5 Years':
  timeframe = 'today 5-y'

number_of_related_queries = st.sidebar.slider('# of Related Keywords', min_value=0, max_value=4, value=2, help='The number of top related keywords to return and compare against your target keyword')

get_data_button = st.sidebar.button('Get Google Trends Data')

#Get Google trends data
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
