import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import SessionState
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
* **Data source:** [NFLfastR](https://github.com/guga31bb/nflfastR-data/).
""")

#Sidebar
st.sidebar.header('User Input Features')

#Sidebar-Select Year
selected_year = st.sidebar.multiselect('Year', list(reversed(range(1990,2021))), default=2020)

# get data for year(s)
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

#Get Player List
@st.cache
def load_players():
    player_csv = pd.read_csv('https://github.com/guga31bb/nflfastR-data/blob/master/data/player_stats.csv.gz?raw=True', 
            compression='gzip', low_memory=False)
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

@st.cache
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


threshhold = st.sidebar.slider('Minimum Play Threshhold', min_value=1, max_value=200)


# Filtering data
stat_columns = [ 'week', 'fantasy', 'posteam', 'posteam_type', 'defteam','yardline_100', 	'game_date', 	'qtr', 	'down', 	'goal_to_go', 	'yrdln', 	'ydstogo', 	'play_type', \
    	'yards_gained', 	'shotgun', 	'no_huddle', 	'qb_dropback', 	'pass_length', 	'pass_location', 	'air_yards', 	'yards_after_catch', 	'run_location', \
            	'run_gap', 	'posteam_score', 	'defteam_score', 	'score_differential', 	'epa', 	'wp', 	'passer_player_name', 	'passing_yards', 	'receiver_player_name', \
                    	'receiving_yards', 	'rusher_player_name', 	'rushing_yards', 	'season', 	'cp', 	'cpoe', 	'stadium', 	'weather', 	'roof', 	'surface', 	'success', 	'qb_epa', ]

@st.cache
def rawdataget(players, team, pos, week, wp, downs, airyards, togo, scoredelt):
    data = pd.DataFrame()

    for i in range(len(selected_player_group)):
        if selected_pos == ['Qb'] or selected_pos == ['Wr/Te']:
            i_all_filters = playerstats[(playerstats['posteam'].isin(team)) & \
                (playerstats['week'].isin(week)) & \
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
                (playerstats['wp'] >= win_perc[0]) & (playerstats['wp'] <= win_perc[1]) & \
                (playerstats['down'].isin(downs_selected)) &\
                (playerstats['ydstogo'] >= togo[0]) & (playerstats['ydstogo'] <= togo[1]) &\
                (playerstats['score_differential'] >= scoredelt[0]) & (playerstats['score_differential'] <= scoredelt[1]) &\
                (playerstats['passer_player_id'].isin([selected_player_group[i]]) | \
                playerstats['rusher_player_id'].isin([selected_player_group[i]]) | playerstats['receiver_player_id'].isin([selected_player_group[i]]))]

        data = data.append(i_all_filters, ignore_index=True)

    return data


# st.write('Data Dimension: ' + str(df_all_filters.shape[0]) + ' rows and ' + str(df_all_filters.shape[1]) + ' columns.')
if selected_player[0] not in ['All Qb', 'All Wr/Te', 'All Rb'] :
    print('selected', selected_player[0])
    if st.button('View Raw Data'):
        raw_data = rawdataget(selected_player_group, selected_team, selected_pos\
        , selected_week, win_perc, downs_selected, air_yards, togo_yards, score_delta)
        st.dataframe(raw_data[stat_columns].sort_values('game_date'))


stat_totals = pd.DataFrame()

@st.cache
def addplayergroup(players, team, pos, week, wp, downs, airyards, togo,
 scoredelt, threshhold):
    data = pd.DataFrame()
    for i in range(len(selected_player_group)):
        print(selected_player_group[i])
        if selected_pos == ['Qb'] or selected_pos == ['Wr/Te']:
            i_all_filters = playerstats[(playerstats['posteam'].isin(team)) & \
                (playerstats['week'].isin(week)) & \
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
                (playerstats['wp'] >= win_perc[0]) & (playerstats['wp'] <= win_perc[1]) & \
                (playerstats['down'].isin(downs_selected)) &\
                (playerstats['ydstogo'] >= togo[0]) & (playerstats['ydstogo'] <= togo[1]) &\
                (playerstats['score_differential'] >= scoredelt[0]) & (playerstats['score_differential'] <= scoredelt[1]) &\
                (playerstats['passer_player_id'].isin([selected_player_group[i]]) | \
                playerstats['rusher_player_id'].isin([selected_player_group[i]]) | playerstats['receiver_player_id'].isin([selected_player_group[i]]))]

        if i_all_filters['play_id'].count() < threshhold:
            i_data = pd.DataFrame()
            group_player_data = data

        else:
            
            netyards = i_all_filters['yards_gained'].sum()
            rushyards = i_all_filters['rushing_yards'].sum()
            playcnt = i_all_filters['week'].count()
            rushes = i_all_filters['rushing_yards'].count()
            epa_mean = i_all_filters['epa'].mean()

            if selected_pos == ['Qb']:
                player_name = i_all_filters['passer_player_name'].mode()
                player_name = str(player_name[0])
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

            elif selected_pos == ['Rb']:
                player_name = i_all_filters['rusher_player_name'].mode()
                player_name = str(player_name[0])
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

            elif selected_pos == ['Wr/Te']:
                player_name = i_all_filters['receiver_player_name'].mode()
                player_name = str(player_name[0])
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

            rushes = i_all_filters['rushing_yards'].count()
            ypplay = (netyards / playcnt)
            if rushes != 0:
                ypc = (rushyards / rushes)
            elif rushes == 0:
                ypc = 0
                
            netepa = i_all_filters['epa'].sum()
            success_perc = ((i_all_filters['success'].sum()) / (i_all_filters['epa'].count()))     
                
                
            i_data = pd.DataFrame({'Player Name': [player_name], 'EPA avg': [epa_mean],
            'Net Yards': [netyards], 'Pass Yards': [passyards], 'Rush Yards': [rushyards], 'Receiving yards': [recyards], 
            'Pass atmps': [passes], 'Rush atmps': [rushes], 'Targets': [trgts], 'Receptions': [receptions],
            'Yards/Play': [ypplay], 'yards/pass': [ypa], 'yards/rush': [ypc], 'yards/catch': [ypcatch],
            'yards/target': [ypt], 'Net EPA': [netepa], 'Success %': [success_perc], 'Comp %': [comp_perc], 'CPOE': [cpoe]})

            data = data.append(i_data, ignore_index=True)
            group_player_data = data

    return group_player_data




if st.button('Create Stat Chart'):
    group_player_df = addplayergroup(selected_player_group, selected_team, selected_pos\
        , selected_week, win_perc, downs_selected, air_yards, togo_yards, score_delta, threshhold)
    st.dataframe(group_player_df)

    raw_data = rawdataget(selected_player_group, selected_team, selected_pos\
        , selected_week, win_perc, downs_selected, air_yards, togo_yards, score_delta)
    
    st.write('Found data from ' + str(raw_data.shape[0]) + 
    ' Plays and ' + str(group_player_df.shape[0]) + ' players')



session_state = SessionState.get(a=0)

# add_player_button = st.button('Create Player Totals Chart')
# if add_player_button:
#     session_state.a = addplayer(selected_player)
#     st.dataframe(session_state.a)

# if st.button('Add current player to new row'):
#     new_data = addplayer(selected_player)
#     session_state.a = session_state.a.append(new_data)
#     st.dataframe(session_state.a)

if st.button('Clear data'):
    session_state.a = 0
    

x_axis_choice = st.selectbox('X Axis choice', ['EPA avg', 'Net Yards', 'Pass Yards', 'Rush Yards',
'Receiving yards', 'Pass atmps', 'Rush atmps', 'Targets', 'Receptions', 
'Yards/Play', 'yards/pass', 'yards/rush', 'yards/catch',
'yards/target', 'Net EPA', 'Success %', 'Comp %', 'CPOE'], index=1)

y_axis_choice = st.selectbox('Y Axis choice', ['EPA avg', 'Net Yards', 'Pass Yards', 'Rush Yards',
'Receiving yards', 'Pass atmps', 'Rush atmps', 'Targets', 'Receptions', 
'Yards/Play', 'yards/pass', 'yards/rush', 'yards/catch',
'yards/target', 'Net EPA', 'Success %', 'Comp %', 'CPOE'], index=9)

# future feature add color gradient
# color = st.selectbox('Color Gradient', ['None', 'EPA avg', 'Net Yards', 'Pass Yards', 'Rush Yards',
# 'Receiving yards', 'Pass atmps', 'Rush atmps', 'Targets', 'Receptions', 
# 'Yards/Play', 'yards/pass', 'yards/rush', 'yards/catch',
# 'yards/target', 'Net EPA', 'Success %', 'Comp %', 'CPOE'], index=0)


if st.button('Draw Graph'):
    
    group_player_df = addplayergroup(selected_player_group, selected_team, selected_pos\
        , selected_week, win_perc, downs_selected, air_yards, togo_yards, score_delta, threshhold)
    st.dataframe(group_player_df)

    names = group_player_df['Player Name']

    
    c = alt.Chart(group_player_df).mark_circle(size=50).encode(
        alt.X(x_axis_choice,
            scale=alt.Scale(
                clamp=True,
            )
        ),
        y=y_axis_choice, tooltip='Player Name').interactive()


    st.altair_chart(c.properties(width=700, height=400))









    
    