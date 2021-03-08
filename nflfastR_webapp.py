import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import SessionState


st.title('NFLfastR Explorer')

st.markdown("""
This app performs simple filtering of NFLfastR data.
* **Upcoming features:** 
filter by posistion, score differential, down, yardline, quarter, air yards, and weather
get totals for all collumns after filter
*compare totals for selected players
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn
* **Data source:** [pro-football-reference.com](https://github.com/guga31bb/nflfastR-data/).
""")

st.sidebar.header('User Input Features')
selected_year = st.sidebar.multiselect('Year', list(reversed(range(1990,2021))), default=2020)

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


# position
position_list = st.sidebar.selectbox('Position', ['None', 'Rb', 'Qb', 'Wr/Te'])
selected_pos = [position_list]

# Sidebar - Player selection

player_list = []

if selected_pos == ['Rb']:
    rusher_list = df_selected_team['rusher_player_name'].dropna()
    player_list = rusher_list
    player_list = player_list.unique()

elif selected_pos == ['Qb']:
    passer_list = df_selected_team['passer_player_name'].dropna()
    player_list = passer_list
    player_list = player_list.unique()
elif selected_pos == ['Wr/Te']:
    receiver_list = df_selected_team['receiver_player_name'].dropna()
    player_list = receiver_list
    player_list = player_list.unique()
else: selected_pos = []


# Sidebar - Player
selected_player = st.sidebar.selectbox('Player', list(sorted(player_list)))
selected_player = [selected_player]

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
st.header('Display Play Results of ' + str(selected_player[0]))
st.write('Data Dimension: ' + str(df_all_filters.shape[0]) + ' rows and ' + str(df_all_filters.shape[1]) + ' columns.')
if st.button('View Raw Data'):
    st.dataframe(df_all_filters[stat_columns].sort_values('game_date'))

# stat variables

if bool(selected_player) == True:

    netyards = df_all_filters['yards_gained'].sum()
    rushyards = df_all_filters['rushing_yards'].sum()
    playcnt = df_all_filters['week'].count()
    rushes = df_all_filters['rushing_yards'].count()
    epa_mean = df_all_filters['epa'].mean()
    
    if selected_pos == ['Qb']:
        passyards = df_all_filters['passing_yards'].sum()
        passes = df_all_filters['air_yards'].count()
        completions = df_all_filters['passing_yards'].count()
        ypa = (passyards / passes)
        comp_perc = (completions / passes)
        cpoe = df_all_filters['cpoe'].mean()
        ypcatch = 'na'
        recyards = 'na'
        ypt = 'na'
        trgts = 'na'
        receptions = 'na'

    elif selected_pos == ['Rb'] or ['Wr/Te']:
        passyards = 'na'
        passes = 'na'
        completions = 'na'
        ypa = 'na'      
        recyards = df_all_filters['receiving_yards'].sum()
        trgts = df_all_filters['air_yards'].count()
        receptions = df_all_filters['receiving_yards'].count() 
        ypt = (recyards / trgts)
        ypcatch = (recyards / receptions)
        comp_perc = 'na'
        cpoe = 'na'  
    
        

    rushes = df_all_filters['rushing_yards'].count()
    ypplay = (netyards / playcnt)
    if rushes != 0:
        ypc = (rushyards / rushes)
    elif rushes == 0:
        ypc = 0
    
    netepa = df_all_filters['epa'].sum()
    success_perc = ((df_all_filters['success'].sum()) / (df_all_filters['epa'].count()))


elif bool(selected_player) == False:
    netyards = 0
    passyards = 0 
    passes= 0
    completions = 0
    passyards = 0
    completions = 0
    rushyards = 0
    recyards = 0
    trgts = 0
    receptions = 0
    rushes = 0 
    playcnt = 0
    ypplay = 0
    ypa = 0
    ypr = 0
    ypt = 0
    ypc = 0
    ypcatch = 0
    netepa = 0
    success_perc = 0
    comp_perc = 0
    cpoe = 0
    



# ADd player to totals chart

stat_totals = pd.DataFrame()

@st.cache
def addplayer(player):
        added_player = str(selected_player[0])
        player_data = pd.DataFrame({'Player Name': [added_player], 
        'Net Yards': [netyards], 'Pass Yards': [passyards], 'Rush Yards': [rushyards], 'Receiving yards': [recyards], 
        'Pass atmps': [passes], 'Rush atmps': [rushes], 'Targets': [trgts], 'Receptions': [receptions],
        'Net ypp': [ypplay], 'yards/pass': [ypplay], 'yards/rush': [ypc], 'yards/catch': [ypcatch],
        'yards/target': [ypt], 'EPA avg': [epa_mean], 'Net EPA': [netepa], 'Success %': [success_perc], 'Comp %': [comp_perc], 'CPOE': [cpoe]})
                    
        return player_data

# if 'st_player_deltagen' not in globals():
#     st_player_deltagen = 0

session_state = SessionState.get(a=0)

add_player_button = st.button('Create Player Totals Chart')
if add_player_button:
    session_state.a = addplayer(selected_player)
    st.dataframe(session_state.a)

if st.button('Add current player to new row'):
    new_data = addplayer(selected_player)
    session_state.a = session_state.a.append(new_data)
    st.dataframe(session_state.a)

if st.button('Clear data'):
    session_state.a = 0
    

    

    # if type(st_player_deltagen) == 'DeltaGenerator':
    #     player_data = addplayer(selected_player)
    #     st_player_deltagen.add_rows(data=addplayer(selected_player))
    # else:
    #     player_data = addplayer(selected_player)
    #     st_player_deltagen = st.dataframe(player_data)    


# if st.button('add players Data') == True:
#     new_player_data = addplayer(selected_player)
#     player_df.add_rows(data=addplayer(selected_player))

# if st.button('View player totals') == True:
#     player_data = addplayer(selected_player)
#     player_df = st.dataframe(player_data)    
#     player_df.add_rows(data=addplayer(selected_player))
# else :
#     player_data = pd.DataFrame()
#     player_df = st.DataFrame()

# if st.button('add players Data') == True:
#     new_player_data = addplayer(selected_player)
#     player_df.add_rows(data=addplayer(selected_player))



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