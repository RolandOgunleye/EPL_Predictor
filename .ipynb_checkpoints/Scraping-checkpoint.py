#!/usr/bin/env python
# coding: utf-8

# In[128]:


import requests


# In[129]:


standings_url = "https://fbref.com/en/comps/9/Premier-League-Stats"


# In[130]:


datas = requests.get(standings_url)


# In[131]:


datas.text


# In[132]:


from bs4 import BeautifulSoup


# In[133]:


soup = BeautifulSoup(datas.text)


# In[134]:


standings_table = soup.select('table.stats_table')[0]


# In[135]:


links = standings_table.find_all('a')


# In[136]:


links = [l.get("href") for l in links]


# In[137]:


links = [l for l in links if '/squads/' in l]


# In[138]:


links


# In[139]:


team_urls = [f"https://fbref.com{l}" for l in links]


# In[140]:


data = requests.get(team_urls[0])


# In[141]:


import pandas as pd
matches = pd.read_html(data.text, match="Scores & Fixtures")[0]


# In[142]:


soup = BeautifulSoup(data.text)
links = soup.find_all('a')
links = [l.get("href") for l in links]
links = [l for l in links if l and 'all_comps/shooting/' in l]


# In[143]:


data = requests.get(f"https://fbref.com{links[0]}")


# In[144]:


shooting = pd.read_html(data.text, match="Shooting")[0]


# In[145]:


shooting.head()


# In[146]:


shooting.columns = shooting.columns.droplevel()


# In[147]:


team_data = matches.merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date")


# In[148]:


team_data.head()


# In[157]:


years = list(range(2022, 2020, -1))
all_matches = []


# In[158]:


standings_url = "https://fbref.com/en/comps/9/Premier-League-Stats"


# In[159]:


import time
for year in years:
    data = requests.get(standings_url)
    soup = BeautifulSoup(data.text)
    standings_table = soup.select('table.stats_table')[0]

    links = [l.get("href") for l in standings_table.find_all('a')]
    links = [l for l in links if '/squads/' in l]
    team_urls = [f"https://fbref.com{l}" for l in links]
    
    previous_season = soup.select("a.prev")[0].get("href")
    standings_url = f"https://fbref.com{previous_season}"
    
    for team_url in team_urls:
        team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
        data = requests.get(team_url)
        matches = pd.read_html(data.text, match="Scores & Fixtures")[0]
        soup = BeautifulSoup(data.text)
        links = [l.get("href") for l in soup.find_all('a')]
        links = [l for l in links if l and 'all_comps/shooting/' in l]
        data = requests.get(f"https://fbref.com{links[0]}")
        shooting = pd.read_html(data.text, match="Shooting")[0]
        shooting.columns = shooting.columns.droplevel()
        try:
            team_data = matches.merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date")
        except ValueError:
            continue
        team_data = team_data[team_data["Comp"] == "Premier League"]
        
        team_data["Season"] = year
        team_data["Team"] = team_name
        all_matches.append(team_data)
        time.sleep(1)


# In[160]:


len(all_matches)


# In[161]:


match_df = pd.concat(all_matches)


# In[162]:


match_df.columns = [c.lower() for c in match_df.columns]


# In[163]:


match_df


# In[164]:


match_df.to_csv("matches.csv")


# In[ ]:




