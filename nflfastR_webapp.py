import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import altair as alt

# Title Text
st.title('NFLfastR Explorer')

st.markdown("""
This app performs simple filtering of NFLfastR data.
* **Upcoming features:** 
filter by for weather
Add a page for team data 
*compare totals for selected players
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn
* **Data source:** [NFLverse](https://github.com/nflverse/nflverse-data).
""")

#Sidebar
st.sidebar.header('User Input Features')

#Sidebar-Select Year
selected_year = st.sidebar.multiselect('Year', list(reversed(range(1990,2024))), default=2023)

# get data for year(s)
@st.cache_data
def load_data(year):
    data = pd.DataFrame()
    for i in year:
        i_data = pd.read_parquet('https://github.com/nflverse/nflverse-data/releases/download/pbp/' \
            'play_by_play_' + str(i) + '.parquet', engine='pyarrow')
        data = pd.concat([data, i_data], sort=True)
        playerstats = data
    
    return playerstats

playerstats = load_data(selected_year)

#Get Player List
@st.cache_data
def load_players():
    player_csv = pd.read_parquet('https://github.com/nflverse/nflverse-data/releases/download/player_stats/player_stats.parquet', engine='pyarrow')
    player_list = player_csv

    return player_list
    
player_csv = load_players()


#Sidebar Select Position
position_list = st.sidebar.selectbox('Position', ['None', 'Qb', 'Rb', 'Wr/Te'], index=1)
selected_pos = [position_list]


#Sidebar Select Team
selected_team = st.sidebar.multiselect('Team', ['All Teams', 'ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', \
        'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC', 'LA', 'LAC', 'LV', 'MIA', 'MIN', 'NE', 'NO', \
            'NYG', 'NYJ', 'PHI', 'PIT', 'SEA', 'SF', 'TB', 'TEN', 'WAS'], default='All Teams')
if selected_team == ['All Teams']: 
    selected_team = ['All Teams', 'ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', \
        'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC', 'LA', 'LAC', 'LV', 'MIA', 'MIN', 'NE', 'NO', \
            'NYG', 'NYJ', 'PHI', 'PIT', 'SEA', 'SF', 'TB', 'TEN', 'WAS']

# Get lists based on position

df_player_list = player_csv[(player_csv['season'].isin(selected_year))]
df_selected_team = df_player_list[(df_player_list['recent_team'].isin(selected_team))]    
receiver_list = df_selected_team[((df_selected_team['receptions'].gt(5)) & (df_selected_team['carries'].lt(5)))]
rusher_list = df_selected_team[(df_selected_team['carries'].gt(7) & (df_selected_team['completions'].lt(3)))]
passer_list = df_selected_team[(df_selected_team['completions'].gt(5))]

if selected_pos == ['Rb']:
    player_list = rusher_list['player_name'].sort_values()
    player_list = player_list.unique()
    
elif selected_pos == ['Qb']:
    player_list = passer_list['player_name'].sort_values()
    player_list = player_list.unique()

elif selected_pos == ['Wr/Te']:
    receiver_list = df_selected_team[((df_selected_team['receptions'].gt(5)) & (df_selected_team['carries'].lt(3)))]
    player_list = receiver_list['player_name'].sort_values()
    player_list = player_list.unique()

else:
    player_list = df_player_list['player_name'].sort_values()
    player_list = player_list.unique()
    receiver_list = df_selected_team[((df_selected_team['receptions'].gt(5)) &
        (df_selected_team['carries'].lt(3)))]
    receiver_list = receiver_list['player_name'].unique()
    passer_list = df_selected_team[(df_selected_team['completions'].gt(5))]


player_list = player_list.tolist()
  

# Player list filtering and getting ID numberss
df_player_list = player_csv[(player_csv['season'].isin(selected_year))]
df_selected_team = df_player_list[(df_player_list['recent_team'].isin(selected_team))]    
receiver_list = df_selected_team[((df_selected_team['receptions'].gt(5)) & (df_selected_team['carries'].lt(3)))]
receiver_names = receiver_list['player_name'].unique()
receiver_ids = receiver_list['player_id'].unique()
rusher_list = df_selected_team[(df_selected_team['carries'].gt(5) & (df_selected_team['completions'].lt(3)))]
rusher_names = rusher_list['player_name'].unique()
rusher_ids = rusher_list['player_id'].unique()
passer_list = df_selected_team[(df_selected_team['completions'].gt(5))]
passer_names = passer_list['player_name'].unique()
passer_ids = passer_list['player_id'].unique()

  


# Sidebar - Player selection
if selected_pos == ['Qb']:
    select_player_list = ['All Qb'] + player_list
elif selected_pos == ['Rb']:
    select_player_list = ['All Rb'] + player_list 
elif selected_pos == ['Wr/Te']:
    select_player_list = ['All Wr/Te'] + player_list   
else: 
    select_player_list = player_list

@st.cache_data
def getplayerids(selected_player, pos, csv):
    if selected_pos == ['Qb']:
        player_id = passer_list[passer_list['player_name'].isin(selected_player)].iloc[0]
        player_id = player_id['player_id']
    elif selected_pos == ['Rb']:
        player_id = rusher_list[rusher_list['player_name'].isin(selected_player)].iloc[0]
        player_id = player_id['player_id']
    elif selected_pos == ['Wr/Te']:
        player_id = receiver_list[receiver_list['player_name'].isin(selected_player)].iloc[0]
        player_id = player_id['player_id']
    return [str(player_id)] 

# Team filtered
df_selected_team = playerstats[(playerstats['posteam'].isin(selected_team))]

# Sidebar - Player select
player_select = st.sidebar.selectbox('Player', list(select_player_list))
selected_player = [player_select]

if selected_player == ['All Qb']: 
    selected_player_group = list(passer_ids)   
    
elif selected_player == ['All Rb']:
    selected_player_group = list(rusher_ids)

elif selected_player == ['All Wr/Te']:
    selected_player_group = list(receiver_ids)

elif selected_pos == ['Qb'] and selected_player != ['All Qb']:
    selected_player_group = getplayerids(selected_player, selected_pos, passer_list)

elif selected_pos == ['Wr/Te'] and selected_player != ['All Wr/Te']:
    selected_player_group = getplayerids(selected_player, selected_pos, receiver_list)

elif selected_pos == ['Rb'] and selected_player != ['All Rb']:
    selected_player_group = getplayerids(selected_player, selected_pos, rusher_list)

 

# if:
#     selected_player_group = getplayerids(selected_player, selected_pos, passer_list)


# Sidebar - Week Selction
week_list = list(range(1,21))
week_list = ['All Weeks', 'Regular Season', 'Post Season'] + week_list
selected_week = st.sidebar.multiselect('Week', week_list, default=['Regular Season'])
if selected_week == ['All Weeks']:
    selected_week = list(range(1,21))
if selected_week == ['Regular Season']:
    selected_week = list(range(1,17))
if selected_week == ['Post Season']:
    selected_week = list(range(18,21))

# Sidebar - downs
downs_selected = st.sidebar.multiselect('Downs', options=[1, 2, 3, 4], default=[1, 2, 3, 4])



#Sidebar - togo
togo_yards = st.sidebar.select_slider('Yards from 1st', options=list(range(0,101)),
 value=[0, 100])
togo_yards = list(togo_yards)

#Sidebar - Air Yards 
air_yards = st.sidebar.select_slider('Air Yards', options=list(range(0,101)),
 value=[0, 100])
air_yards = list(air_yards)
print(type(air_yards))

#Sidebar - Score differential
score_delta = st.sidebar.select_slider('Score Differential', options=list(range(-50,51)), 
value=[-50,50])
score_delta = list(score_delta)


# Sidebar - win%
win_perc = st.sidebar.select_slider('Win Percentage', options=list(range(0,101)), value=[0, 100])
win_perc = list(win_perc)

#Sidebar - Redzone
redzone_only = st.sidebar.checkbox('Redzone Only (Inside 20)', value=False)

threshhold = st.sidebar.slider('Minimum Play Threshhold', min_value=1, max_value=200)


# Filtering data
stat_columns = [ 'week', 'fantasy', 'posteam', 'posteam_type', 'defteam','yardline_100', 	'game_date', 	'qtr', 	'down', 	'goal_to_go', 	'yrdln', 	'ydstogo', 	'play_type', \
    	'yards_gained', 	'shotgun', 	'no_huddle', 	'qb_dropback', 	'pass_length', 	'pass_location', 	'air_yards', 	'yards_after_catch', 	'run_location', \
            	'run_gap', 	'posteam_score', 	'defteam_score', 	'score_differential', 	'epa', 	'wp', 	'passer_player_name', 	'passing_yards', 	'receiver_player_name', \
                    	'receiving_yards', 	'rusher_player_name', 	'rushing_yards', 	'season', 	'cp', 	'cpoe', 	'stadium', 	'weather', 	'roof', 	'surface', 	'success', 	'qb_epa', ]

@st.cache_data
def rawdataget(players, team, pos, week, wp, downs, airyards, togo, scoredelt, redzone_only=False):
    data = pd.DataFrame()

    for i in range(len(selected_player_group)):
        if selected_pos == ['Qb'] or selected_pos == ['Wr/Te']:
            i_all_filters = playerstats[(playerstats['posteam'].isin(team)) & \
                (playerstats['week'].isin(week)) & \
                (~playerstats['yardline_100'].isna()) & \
                (playerstats['yardline_100'] <= 20 if redzone_only else playerstats['yardline_100'] <= 100) & \
                (playerstats['wp'] >= win_perc[0]) & (playerstats['wp'] <= win_perc[1]) & \
                (playerstats['down'].isin(downs_selected)) & \
                (playerstats['air_yards'] >= air_yards[0]) & (playerstats['air_yards'] <= air_yards[1]) &\
                (playerstats['ydstogo'] >= togo[0]) & (playerstats['ydstogo'] <= togo[1]) &\
                (playerstats['score_differential'] >= scoredelt[0]) & (playerstats['score_differential'] <= scoredelt[1]) &\
                (playerstats['passer_player_id'].isin([selected_player_group[i]]) | \
                playerstats['rusher_player_id'].isin([selected_player_group[i]]) | playerstats['receiver_player_id'].isin([selected_player_group[i]]))]

        elif selected_pos == ['Rb']:
            i_all_filters = playerstats[(playerstats['posteam'].isin(team)) & \
                (playerstats['week'].isin(week)) & \
                (~playerstats['yardline_100'].isna()) & \
                (playerstats['yardline_100'] <= 20 if redzone_only else playerstats['yardline_100'] <= 100) & \
                (playerstats['wp'] >= win_perc[0]) & (playerstats['wp'] <= win_perc[1]) & \
                (playerstats['down'].isin(downs_selected)) &\
                (playerstats['ydstogo'] >= togo[0]) & (playerstats['ydstogo'] <= togo[1]) &\
                (playerstats['score_differential'] >= scoredelt[0]) & (playerstats['score_differential'] <= scoredelt[1]) &\
                (playerstats['passer_player_id'].isin([selected_player_group[i]]) | \
                playerstats['rusher_player_id'].isin([selected_player_group[i]]) | playerstats['receiver_player_id'].isin([selected_player_group[i]]))]

        data = data.append(i_all_filters, ignore_index=True)

    return data


# st.write('Data Dimension: ' + str(df_all_filters.shape[0]) + ' rows and ' + str(df_all_filters.shape[1]) + ' columns.')

tab_player, tab_team, tab_pbp = st.tabs(["Player Stats", "Team Stats", "Play-by-Play Explorer"])

with tab_pbp:
    st.header("Play-by-Play Explorer")
    if selected_player[0] not in ['All Qb', 'All Wr/Te', 'All Rb'] :
        st.write('Selected player:', selected_player[0])
        if st.button('View Raw Data'):
            raw_data = rawdataget(selected_player_group, selected_team, selected_pos, selected_week, win_perc, downs_selected, air_yards, togo_yards, score_delta)
            st.dataframe(raw_data[stat_columns].sort_values('game_date'))

with tab_team:
    st.header("Team Stats")
    st.write("Team stats functionality coming soon.")

with tab_player:
    st.header("Player Stats")
    
    if st.button('Create Stat Chart'):
        group_player_df = addplayergroup(selected_player_group, selected_team, selected_pos, selected_week, win_perc, downs_selected, air_yards, togo_yards, score_delta, threshhold)
        
        if not group_player_df.empty and len(group_player_df) == 1:
            row = group_player_df.iloc[0]
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Net Yards", row['Net Yards'])
            col2.metric("EPA Avg", round(row['EPA avg'], 2) if isinstance(row['EPA avg'], (int, float)) else row['EPA avg'])
            col3.metric("Success %", f"{round(row['Success %']*100, 1)}%" if isinstance(row['Success %'], (int, float)) else row['Success %'])
            col4.metric("Net EPA", round(row['Net EPA'], 2) if isinstance(row['Net EPA'], (int, float)) else row['Net EPA'])

        st.dataframe(group_player_df)
    
        raw_data = rawdataget(selected_player_group, selected_team, selected_pos, selected_week, win_perc, downs_selected, air_yards, togo_yards, score_delta)
        st.write('Found data from ' + str(raw_data.shape[0]) + ' Plays and ' + str(group_player_df.shape[0]) + ' players')

    st.subheader("Visualizations")
    colA, colB = st.columns(2)
    with colA:
        x_axis_choice = st.selectbox('X Axis choice', ['EPA avg', 'Net Yards', 'Pass Yards', 'Rush Yards', 'Receiving yards', 'Pass atmps', 'Rush atmps', 'Targets', 'Receptions', 'Yards/Play', 'yards/pass', 'yards/rush', 'yards/catch', 'yards/target', 'Net EPA', 'Success %', 'Comp %', 'CPOE'], index=1)
    with colB:
        y_axis_choice = st.selectbox('Y Axis choice', ['EPA avg', 'Net Yards', 'Pass Yards', 'Rush Yards', 'Receiving yards', 'Pass atmps', 'Rush atmps', 'Targets', 'Receptions', 'Yards/Play', 'yards/pass', 'yards/rush', 'yards/catch', 'yards/target', 'Net EPA', 'Success %', 'Comp %', 'CPOE'], index=9)
    
    if st.button('Draw Graph'):
        group_player_df = addplayergroup(selected_player_group, selected_team, selected_pos, selected_week, win_perc, downs_selected, air_yards, togo_yards, score_delta, threshhold)
        
        c = alt.Chart(group_player_df).mark_circle(size=50).encode(
            x=alt.X(x_axis_choice, scale=alt.Scale(zero=False)),
            y=alt.Y(y_axis_choice, scale=alt.Scale(zero=False)),
            tooltip=['Player Name', x_axis_choice, y_axis_choice]
        ).interactive()
        
        st.altair_chart(c, use_container_width=True)
