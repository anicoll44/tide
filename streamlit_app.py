import streamlit as st
import pytrends
from pytrends.request import TrendReq
import pandas as pd
import numpy as np
import requests
from datetime import datetime, date, time
from GoogleNews import GoogleNews
from PIL import Image

#Set width of page to fullscreen
st.set_page_config(page_title = 'Project TIDE', initial_sidebar_state = 'expanded', layout="wide", menu_items = {'About': 'Reach out to Andrew Nicoll on Slack'})
image = Image.open('tide_dark.png')
st.sidebar.image(image, width = 180)


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.subheader("Welcome to Project T I D E")
        st.write("TIDE helps automate Google Trends analysis, making it much easier and efficient. It returns data for requested keywords, suggests new keywords, and plots their relative interest over time to help with keyword research, headline optimization, trend shifts, and more.")

        st.text_input(
            "Please enter your password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.subheader("Welcome to Project T I D E")
        st.write("TIDE helps automate Google Trends analysis, making it much easier and efficient. It returns data for requested keywords, suggests new keywords, and plots their relative interest over time to help with keyword research, headline optimization, trend shifts, and more.")
        st.text_input(
            "Please enter your password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():

    #Build sidebar and set request paramaeters
    
    #Enter target keyword
    kw = st.sidebar.text_input('Enter a Target Keyword', '', type = 'default')
    kw_list = [kw]

    #Select timeframe
    timeframe = st.sidebar.selectbox(
        'Timeframe',
        ("Past 1 Hour", "Past 4 Hours", "Past 24 Hours", "Past 7 Days", "Past 30 Days", "Past 90 Days", "Past 12 Months", "Past 5 Years"), index = 4)

    #Map timeframe to google trends requirements
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

    #Select rising query timeframe
    rising_query_timeframe = st.sidebar.selectbox(
        'Rising Keyword Timeframe',
        ("Past 1 Hour", "Past 4 Hours", "Past 24 Hours", "Past 7 Days", "Past 30 Days", "Past 90 Days", "Past 12 Months", "Past 5 Years"), index = 3, help = 'Keywords with the biggest increase in search frequency during this timeframe. Results marked "Breakout" had a tremendous increase, probably because these keywords are new and had few (if any) prior searches.')

    #Map timeframe to google trends requirements
    if rising_query_timeframe == "Past 7 Days":
        rising_query_timeframe = "now 7-d"
    elif rising_query_timeframe == 'Past 1 Hour':
        rising_query_timeframe = 'now 1-H'
    elif rising_query_timeframe == 'Past 4 Hours':
        rising_query_timeframe = 'now 4-H'
    elif rising_query_timeframe == 'Past 24 Hours':
        rising_query_timeframe = 'now 1-d'
    elif rising_query_timeframe == 'Past 30 Days':
        rising_query_timeframe = 'today 1-m'
    elif rising_query_timeframe == 'Past 90 Days':
        rising_query_timeframe = 'today 3-m'
    elif rising_query_timeframe == 'Past 12 Months':
        rising_query_timeframe = 'today 12-m'
    elif rising_query_timeframe == 'Past 5 Years':
        rising_query_timeframe = 'today 5-y'

    #Select number of related queries
    number_of_related_queries = st.sidebar.slider('# of Related Keywords', min_value=0, max_value=4, value=4, help='The number of top related keywords to return and compare against your target keyword')

    #Select number of related news
    #number_of_related_news = st.sidebar.slider('# of Related News Articles', min_value=0, max_value=5, value= 2, help='The number of top keywords to return related news for')

    #Button to trigger getting google trends data
    get_data_button = st.sidebar.button('Get Google Trends Data')

    #Get Google trends data
    if get_data_button:
        pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25), proxies=['https://34.203.233.13:80',], retries=2, backoff_factor=0.1, requests_args={'verify':False})
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
    
        st.markdown('#### Interest Over Time')
        st.line_chart(data=interest_o_time_df)
        
        col1, col2, col3 = st.columns(3)
    
        with col1:
            #get rising queries
            rising_df = list(related_queries.values())[0]['rising']
            rising_df = rising_df.reset_index(drop=True)
            rising_df = rising_df.rename(columns={"query": "Keyword", "value": "% Increase"})
            top_rising_list = rising_df['Keyword'].head(number_of_related_news).tolist()
            
            st.write('')
            st.markdown('###### Rising Related Keywords')
            st.dataframe(data=rising_df)
          
        with col2:
            real_time_trends = pytrends.realtime_trending_searches(pn='US')
            real_time_trends = real_time_trends.drop('entityNames', axis = 1)
            real_time_trends = real_time_trends.rename(columns={"title": "Topic"})
            #real_time_trends['Rank'] = real_time_trends.index + 1
            real_time_list = real_time_trends['Topic'].head(number_of_related_news).tolist()
            
            st.write('')                                           
            st.markdown('###### Realtime Search Trends (US)')
            st.dataframe(real_time_trends)

        with col3:
            trending_df = pytrends.trending_searches(pn='united_states')
            trending_df = trending_df.rename(columns={0: "Keyword"})
            trending_df['Rank'] = trending_df.index + 1
            trending_list = trending_df['Keyword'].head(number_of_related_news).tolist()
            
            st.write('')
            st.markdown('###### Daily Search Trends (US)')
            st.dataframe(data=trending_df)
    
        #Get Google News Data
        #googlenews = GoogleNews()
    
        #Create df to load news data
        #news_df = pd.DataFrame(columns=['title', 'media',	'date',	'datetime',	'desc',	'link',	'img', 'query'])

        #Create list of uniquq tracked keywords and related queries
        #gnews_list = kw_list + top_rising_list + trending_list + real_time_list
        #gset = set(gnews_list)
        #gnews_list = gset

        #Get Google News for each item in list
        #for item in gnews_list:
            #try:
                #googlenews.clear()
                #googlenews.search(item)
                #result = googlenews.results()
                #temp_news_df = pd.DataFrame(result)
                #temp_news_df['query'] = item
                #news_df = news_df.append(temp_news_df, ignore_index=True)
            #except requests.exceptions.Timeout:
                #st.write('Timeout occured, please try again')
    
        #Cleanup and show news df
        #news_df = news_df.drop_duplicates()
        #news_df = news_df.drop(columns=['img','media','datetime','desc'])
        #news_df = news_df.rename(columns={"title": "Title", "date": "Date", "link": "URL", "query": "Keyword"})
        #st.write('')   
        #st.markdown('###### Related News')
        st.dataframe(data=news_df, height=800)
