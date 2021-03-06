import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.title('NFLfastR Explorer')

st.markdown("""
This app performs simple filtering of NFLfastR data.
* **Upcoming features:** 
filter by posistion, score differential, down, yardline, quarter, air yards, and weather
get totals for all collumns after filter
*compare totals for selected players
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn
* **Data source:** [pro-football-reference.com](https://www.pro-football-reference.com/).
""")

st.sidebar.header('User Input Features')
selected_year = st.sidebar.multiselect('Year', list(reversed(range(1990,2021))), default=2020)
print(selected_year)

# Web scraping of NFL player stats
# https://www.pro-football-reference.com/years/2019/rushing.htm



@st.cache
def load_data(year):
    data = pd.DataFrame()
    for i in selected_year:
        i_data = pd.read_csv('https://github.com/guga31bb/nflfastR-data/blob/master/data/' \
            'play_by_play_' + str(i) + '.csv.gz?raw=True', 
            compression='gzip', low_memory=False)
        data = data.append(i_data, sort=True)
        playerstats = data
    
    return playerstats


playerstats = load_data(selected_year)

print(playerstats['game_date'].unique())


# Sidebar - Team selection
team_list = playerstats['posteam'].dropna()
sorted_unique_team = sorted(team_list.unique())
sorted_unique_team = ['All Teams'] + sorted_unique_team
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)


if selected_team == ['All Teams']: 
    selected_team = ['All Teams', 'ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', \
        'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC', 'LA', 'LAC', 'LV', 'MIA', 'MIN', 'NE', 'NO', \
            'NYG', 'NYJ', 'PHI', 'PIT', 'SEA', 'SF', 'TB', 'TEN', 'WAS']

# Team filtered
df_selected_team = playerstats[(playerstats['posteam'].isin(selected_team))]

# Sidebar - Player selection
passer_list = df_selected_team['passer_player_name'].dropna()
rusher_list = df_selected_team['rusher_player_name'].dropna()
receiver_list = df_selected_team['receiver_player_name'].dropna()
player_list = passer_list.append(rusher_list)
player_list = player_list.append(receiver_list)
player_list = player_list.unique()

# Sidebar - Player
selected_player = st.sidebar.multiselect('Player', list(sorted(player_list)))

# Sidebar - Week Selction
week_list = list(range(1,21))
week_list = ['All Weeks'] + week_list
selected_week = st.sidebar.multiselect('Week', week_list, default=['All Weeks'])
if selected_week == ['All Weeks']:
    selected_week = list(range(1,21))

# Sidebar - win%

win_perc_filter = st.sidebar.select_slider('Win Percentage', options=list(range(0,101)), value=[0, 100])

win_perc_filter = list(win_perc_filter)

win_perc_filter_max = (win_perc_filter[1] / 100)
win_perc_filter_min = (win_perc_filter[0] / 100)



# Filtering data
stat_columns = [ 'week', 'fantasy', 'posteam', 'posteam_type', 'defteam','yardline_100', 	'game_date', 	'qtr', 	'down', 	'goal_to_go', 	'yrdln', 	'ydstogo', 	'play_type', \
    	'yards_gained', 	'shotgun', 	'no_huddle', 	'qb_dropback', 	'pass_length', 	'pass_location', 	'air_yards', 	'yards_after_catch', 	'run_location', \
            	'run_gap', 	'posteam_score', 	'defteam_score', 	'score_differential', 	'epa', 	'wp', 	'passer_player_name', 	'passing_yards', 	'receiver_player_name', \
                    	'receiving_yards', 	'rusher_player_name', 	'rushing_yards', 	'season', 	'cp', 	'cpoe', 	'stadium', 	'weather', 	'roof', 	'surface', 	'success', 	'qb_epa', ]
#apply filters
df_all_filters = playerstats[(playerstats['posteam'].isin(selected_team)) & \
    (playerstats['week'].isin(selected_week)) & \
        (playerstats['wp'] >= win_perc_filter_min) & (playerstats['wp'] <= win_perc_filter_max) & \
        (playerstats['passer_player_name'].isin(selected_player) | \
        playerstats['rusher_player_name'].isin(selected_player) | playerstats['receiver_player_name'].isin(selected_player))]



# df_selected_week = df_selected_team[(df_selected_team['week'].isin(selected_week))]
st.header('Display Player Stats of Selected Team(s)')
st.write('Data Dimension: ' + str(df_all_filters.shape[0]) + ' rows and ' + str(df_all_filters.shape[1]) + ' columns.')
st.dataframe(df_all_filters[stat_columns].sort_values('game_date'))

# Download NBA player stats data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

# Heatmap
# if st.button('Intercorrelation Heatmap'):
#     st.header('Intercorrelation Matrix Heatmap')
#     df_selected_team.to_csv('output.csv',index=False)
#     df = pd.read_csv('output.csv')

#     corr = df.corr()
#     mask = np.zeros_like(corr)
#     mask[np.triu_indices_from(mask)] = True
#     with sns.axes_style("white"):
#         f, ax = plt.subplots(figsize=(7, 5))
#         ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
#     st.pyplot()