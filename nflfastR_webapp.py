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
selected_year = st.sidebar.multiselect('Year', list(reversed(range(1990,2026))), default=2025)

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
    player_list = rusher_list['player_name'].sort_values().unique()
    
elif selected_pos == ['Qb']:
    player_list = passer_list['player_name'].sort_values().unique()

elif selected_pos == ['Wr/Te']:
    receiver_list = df_selected_team[((df_selected_team['receptions'].gt(5)) & (df_selected_team['carries'].lt(3)))]
    player_list = receiver_list['player_name'].sort_values().unique()

else:
    player_list = df_player_list['player_name'].sort_values().unique()
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
def addplayergroup(players, team, pos, week, wp, downs, airyards, togo, scoredelt, threshhold, redzone_only=False):
    data = pd.DataFrame()
    for i in range(len(players)):
        if pos == ['Qb'] or pos == ['Wr/Te']:
            i_all_filters = playerstats[(playerstats['posteam'].isin(team)) & \
                (playerstats['week'].isin(week)) & \
                (~playerstats['yardline_100'].isna()) & \
                (playerstats['yardline_100'] <= 20 if redzone_only else playerstats['yardline_100'] <= 100) & \
                (playerstats['wp'] >= wp[0]) & (playerstats['wp'] <= wp[1]) & \
                (playerstats['down'].isin(downs)) & \
                (playerstats['air_yards'] >= airyards[0]) & (playerstats['air_yards'] <= airyards[1]) &\
                (playerstats['ydstogo'] >= togo[0]) & (playerstats['ydstogo'] <= togo[1]) &\
                (playerstats['score_differential'] >= scoredelt[0]) & (playerstats['score_differential'] <= scoredelt[1]) &\
                (playerstats['passer_player_id'].isin([players[i]]) | \
                playerstats['rusher_player_id'].isin([players[i]]) | playerstats['receiver_player_id'].isin([players[i]]))]

        elif pos == ['Rb']:
            i_all_filters = playerstats[(playerstats['posteam'].isin(team)) & \
                (playerstats['week'].isin(week)) & \
                (~playerstats['yardline_100'].isna()) & \
                (playerstats['yardline_100'] <= 20 if redzone_only else playerstats['yardline_100'] <= 100) & \
                (playerstats['wp'] >= wp[0]) & (playerstats['wp'] <= wp[1]) & \
                (playerstats['down'].isin(downs)) &\
                (playerstats['ydstogo'] >= togo[0]) & (playerstats['ydstogo'] <= togo[1]) &\
                (playerstats['score_differential'] >= scoredelt[0]) & (playerstats['score_differential'] <= scoredelt[1]) &\
                (playerstats['passer_player_id'].isin([players[i]]) | \
                playerstats['rusher_player_id'].isin([players[i]]) | playerstats['receiver_player_id'].isin([players[i]]))]

        if i_all_filters['play_id'].count() < threshhold:
            pass
        else:
            netyards = i_all_filters['yards_gained'].sum()
            rushyards = i_all_filters['rushing_yards'].sum()
            playcnt = i_all_filters['week'].count()
            rushes = i_all_filters['rushing_yards'].count()
            epa_mean = i_all_filters['epa'].mean()

            if pos == ['Qb']:
                player_name = i_all_filters['passer_player_name'].mode()
                player_name = str(player_name[0]) if len(player_name)>0 else "Unknown"
                passyards = i_all_filters['passing_yards'].sum()
                passes = i_all_filters['air_yards'].count()
                completions = i_all_filters['passing_yards'].count()
                if passes != 0:
                    ypa = (passyards / passes)
                    comp_perc = (completions / passes)
                else:
                    ypa = 0
                    comp_perc = 0
                cpoe = i_all_filters['cpoe'].mean()
                ypcatch = 'na'
                recyards = 'na'
                ypt = 'na'
                trgts = 'na'
                receptions = 'na'

            elif pos == ['Rb']:
                player_name = i_all_filters['rusher_player_name'].mode()
                player_name = str(player_name[0]) if len(player_name)>0 else "Unknown"
                passyards = 'na'
                passes = 'na'
                completions = 'na'
                ypa = 'na'      
                recyards = i_all_filters['receiving_yards'].sum()
                trgts = i_all_filters['air_yards'].count()
                receptions = i_all_filters['receiving_yards'].count() 
                if trgts != 0:
                    ypt = (recyards / trgts)
                else:
                    ypt = 0
                if receptions != 0:
                    ypcatch = (recyards / receptions)
                else:
                    ypcatch = 0
                comp_perc = 'na'
                cpoe = 'na'  

            elif pos == ['Wr/Te']:
                player_name = i_all_filters['receiver_player_name'].mode()
                player_name = str(player_name[0]) if len(player_name)>0 else "Unknown"
                passyards = 'na'
                passes = 'na'
                completions = 'na'
                ypa = 'na'      
                recyards = i_all_filters['receiving_yards'].sum()
                trgts = i_all_filters['air_yards'].count()
                receptions = i_all_filters['receiving_yards'].count() 
                if trgts != 0:
                    ypt = (recyards / trgts)
                else:
                    ypt = 0
                if receptions != 0:
                    ypcatch = (recyards / receptions)
                else:
                    ypcatch = 0
                comp_perc = 'na'
                cpoe = 'na'                    

            ypplay = (netyards / playcnt) if playcnt != 0 else 0
            
            p_data = pd.DataFrame({'Player Name': [player_name], 'EPA avg': [epa_mean], 'Net Yards': [netyards], 
                                   'Pass Yards': [passyards], 'Rush Yards': [rushyards], 
                                   'Receiving yards': [recyards], 'Pass atmps': [passes], 
                                   'Rush atmps': [rushes], 'Targets': [trgts], 'Receptions': [receptions], 
                                   'Yards/Play': [ypplay], 'yards/pass': [ypa], 'yards/rush': [0], 
                                   'yards/catch': [ypcatch], 'yards/target': [ypt], 'Net EPA': [0], 
                                   'Success %': [0], 'Comp %': [comp_perc], 'CPOE': [cpoe]})
            data = pd.concat([data, p_data], ignore_index=True)
            
    return data

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

        data = pd.concat([data, i_all_filters], ignore_index=True)

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
    st.write("Compare Offensive vs Defensive EPA for selected teams.")
    
    if st.button("Calculate Team EPA"):
        # We need to compute team offensive EPA (posteam = team) and defensive EPA (defteam = team)
        team_epa_list = []
        for team in selected_team:
            if team == 'All Teams': continue
            
            # Offense
            off_plays = playerstats[
                (playerstats['posteam'] == team) & 
                (playerstats['week'].isin(selected_week)) &
                (~playerstats['yardline_100'].isna()) & 
                (playerstats['yardline_100'] <= 20 if redzone_only else playerstats['yardline_100'] <= 100) & 
                (playerstats['wp'] >= win_perc[0]) & (playerstats['wp'] <= win_perc[1]) & 
                (playerstats['down'].isin(downs_selected)) &
                (playerstats['ydstogo'] >= togo_yards[0]) & (playerstats['ydstogo'] <= togo_yards[1]) &
                (playerstats['score_differential'] >= score_delta[0]) & (playerstats['score_differential'] <= score_delta[1])
            ]
            
            # Defense
            def_plays = playerstats[
                (playerstats['defteam'] == team) & 
                (playerstats['week'].isin(selected_week)) &
                (~playerstats['yardline_100'].isna()) & 
                (playerstats['yardline_100'] <= 20 if redzone_only else playerstats['yardline_100'] <= 100) & 
                (playerstats['wp'] >= win_perc[0]) & (playerstats['wp'] <= win_perc[1]) & 
                (playerstats['down'].isin(downs_selected)) &
                (playerstats['ydstogo'] >= togo_yards[0]) & (playerstats['ydstogo'] <= togo_yards[1]) &
                (playerstats['score_differential'] >= score_delta[0]) & (playerstats['score_differential'] <= score_delta[1])
            ]
            
            off_epa = off_plays['epa'].mean()
            def_epa = def_plays['epa'].mean() # Note: For defense, negative EPA is good
            
            team_epa_list.append({
                'Team': team,
                'Offensive EPA/play': off_epa,
                'Defensive EPA/play': def_epa,
                'Net EPA/play': off_epa - def_epa if off_epa is not None and def_epa is not None else None
            })
            
        if team_epa_list:
            team_epa_df = pd.DataFrame(team_epa_list)
            st.dataframe(team_epa_df)
            
            chart = alt.Chart(team_epa_df).mark_circle(size=100).encode(
                x=alt.X('Offensive EPA/play', title='Offensive EPA/Play'),
                y=alt.Y('Defensive EPA/play', title='Defensive EPA/Play (Lower is better)', scale=alt.Scale(reverse=True)),
                tooltip=['Team', 'Offensive EPA/play', 'Defensive EPA/play', 'Net EPA/play']
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)

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
            x=alt.X(f"{x_axis_choice}:Q", scale=alt.Scale(zero=False)),
            y=alt.Y(f"{y_axis_choice}:Q", scale=alt.Scale(zero=False)),
            tooltip=['Player Name:N', f"{x_axis_choice}:Q", f"{y_axis_choice}:Q"]
        ).interactive()
        
        st.altair_chart(c, use_container_width=True)
