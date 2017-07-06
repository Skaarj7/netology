# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 18:59:41 2017

@author: Skaarj
"""

import numpy as np
import pandas as pd

# загружаем данные
players = pd.read_csv('data/Players.csv')
seasons = pd.read_csv('data/Seasons_Stats.csv')

# дропаем первые ненужные колонки в обоих сетах
players.drop(players.columns[0], axis=1, inplace=True)
seasons.drop(seasons.columns[0], axis=1, inplace=True)

# удаляем строки без имени игрока
seasons = seasons[pd.notnull(seasons.Player)]

# добавляем в seasons дату из players
seasons['height'] = seasons.Player.apply(lambda x: players.height[players.Player == x].values[0])
seasons['weight'] = seasons.Player.apply(lambda x: players.weight[players.Player == x].values[0])

# посчитаем ндекс массы тела
seasons['bmi'] = seasons['weight'] / np.power(seasons['height']/100,2)

# удаляем дату с пропущенными значениями
seasons.dropna(axis=1, inplace=True)


# добавим колонку для учета очков, набранных в среднем за игру
seasons['pts_per_game'] = seasons['PTS'] / seasons['G']

# пробуем matplotlib
import matplotlib.pyplot as plt

# сначала посмотрим как выглядели распределния роста и веса по декадам
data_height = []
data_weight = []
data_bmi = []
for i in range(1950,2020,10):
    data_height.append(seasons.height[(seasons.Year >= i) & (seasons.Year < i+10) & (seasons.Tm == 'TOT')])
    data_weight.append(seasons.weight[(seasons.Year >= i) & (seasons.Year < i+10) & (seasons.Tm == 'TOT')])
    data_bmi.append(seasons.bmi[(seasons.Year >= i) & (seasons.Year < i+10) & (seasons.Tm == 'TOT')])

# рост игроков
plt.boxplot(data_height)
plt.xticks([1,2,3,4,5,6,7], ['50s','60s','70s','80s','90s','2000s','2010s'])
plt.ylabel('Height [cm]')
plt.xlabel('Decade')

# вес игроков
plt.boxplot(data_weight)
plt.xticks([1,2,3,4,5,6,7], ['50s','60s','70s','80s','90s','2000s','2010s'])
plt.ylabel('Weight [kg]')
plt.xlabel('Decade')

# индекс массы тела
plt.boxplot(data_bmi)
plt.xticks([1,2,3,4,5,6,7], ['50s','60s','70s','80s','90s','2000s','2010s'])
plt.ylabel('BMI [points]')
plt.xlabel('Decade')


# TOP-10 игроков по очкам за одну игру
top_players = seasons.groupby('Player')[['pts_per_game']].mean().sort_values('pts_per_game', ascending=False)
top10 = top_players.head(10)
top10.style.bar()


# попробуем seaborn
import seaborn as sns

# посмотрим на распределение набранных очков за одну игру
sns.distplot(seasons['pts_per_game'])




# посмотрим на статистику набора очков TOP-10 игроков
with sns.color_palette("Paired", 11):
    plt.figure(figsize = (10,10))
    plt.plot(seasons.Year.unique(), seasons.groupby('Year')[['pts_per_game']].mean())
    for i in range(10):
        plt.plot(seasons.Year[seasons.Player == top10.index[i]], seasons.pts_per_game[seasons.Player == top10.index[i]])
    
    plt.legend(['Median Player'] + list(top10.index.values), fontsize = 10)
    plt.xlabel('Year')
    plt.ylabel('Points Per Game')
    plt.title('Points Leaders')

# посмотрим корреляцию между количеством совершенных бросков (удачных и неудачных) и набранными очками
sns.jointplot(x=seasons.FGA/seasons.G, y=seasons.pts_per_game, kind='reg')\
    .set_axis_labels("Field Goal Attempts per Game", "Points per Game")
sns.plt.show()

# поиграем с Plotly

# поиграем с Plotly
from plotly.offline import init_notebook_mode, iplot

import pandas as pd

init_notebook_mode(connected=True)

years = seasons.Year.apply(int).unique()

# make list of positions
positions = []
for position in seasons['Pos']:
    if position not in positions:
        positions.append(position)
        
# make figure
figure = {
    'data': [],
    'layout': {},
    'frames': []
}

# fill figure layouts
figure['layout']['xaxis'] = {'title': 'Weight', 'range': [50, 170], 'autorange': False}
figure['layout']['yaxis'] = {'title': 'Height', 'range': [130, 250], 'autorange': False}
figure['layout']['hovermode'] = 'closest'
figure['layout']['updatemenus'] = [
    {
        'buttons': [
            {
                'args': [None, {'frame': {'duration': 500, 'redraw': False},
                         'fromcurrent': True, 'transition': {'duration': 300, 'easing': 'quadratic-in-out'}}],
                'label': 'Play',
                'method': 'animate'
            },
            {
                'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate',
                'transition': {'duration': 0}}],
                'label': 'Pause',
                'method': 'animate'
            }
        ],
        'direction': 'left',
        'pad': {'r': 10, 't': 87},
        'showactive': False,
        'type': 'buttons',
        'x': 0.1,
        'xanchor': 'right',
        'y': 0,
        'yanchor': 'top'
    }
]

sliders_dict = {
    'active': 0,
    'yanchor': 'top',
    'xanchor': 'left',
    'currentvalue': {
        'font': {'size': 20},
        'prefix': 'Year:',
        'visible': True,
        'xanchor': 'right'
    },
    'transition': {'duration': 300, 'easing': 'cubic-in-out'},
    'pad': {'b': 10, 't': 50},
    'len': 0.9,
    'x': 0.1,
    'y': 0,
    'steps': []
}

# make init data
year = 1950
for position in positions:
    seasons_by_year = seasons[seasons['Year'] == year]
    seasons_by_year_and_team = seasons_by_year[seasons_by_year['Pos'] == position]

    data_dict = {
        'x': list(seasons_by_year_and_team['weight']),
        'y': list(seasons_by_year_and_team['height']),
        'mode': 'markers',
        'text': list(seasons_by_year_and_team['Player']),
        'name': str(position)
    }
    figure['data'].append(data_dict)
    
# make frames data
for year in years:
    frame = {'data': [], 'name': str(year)}
    for position in positions:
        seasons_by_year = seasons[seasons['Year'] == int(year)]
        seasons_by_year_and_team = seasons_by_year[seasons_by_year['Pos'] == position]

        data_dict = {
            'x': list(seasons_by_year_and_team['weight']),
            'y': list(seasons_by_year_and_team['height']),
            'mode': 'markers',
            'text': list(seasons_by_year_and_team['Player']),
            'name': str(position)
        }
        frame['data'].append(data_dict)

    figure['frames'].append(frame)
    slider_step = {'args': [
        [year],
        {'frame': {'duration': 300, 'redraw': False},
         'mode': 'immediate',
         'transition': {'duration': 300}}
     ],
     'label': year,
     'method': 'animate'}
    sliders_dict['steps'].append(slider_step)

figure['layout']['sliders'] = [sliders_dict]


# получаем график как менялся вес-рост игроков по годам с привязкой к позиции, которую они занимают на площадке
iplot(figure)