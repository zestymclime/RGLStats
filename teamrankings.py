import pystan
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pickle

def predict_rounds(mapname,scores,team_a,team_b,rounds_data):
    """
    Big Uncommented function for plotting match predictions.
    This doesn't work very well, maybe I'll clean this up in future.
    """
    teamslist=rounds_data.blu_team.unique()
    n_teams=len(teamslist)
    team_a_score=scores[:,teamslist==team_a]
    team_b_score=scores[:,teamslist==team_b]
    winroundprobs=1/(1+np.exp(team_b_score-team_a_score))
    minround=min(rounds_data[rounds_data['map']==mapname]['round_duration'])
    mapvalue=int(numbers_map[mapname])+1

    durations=np.random.gamma(shapes_array[mapvalue-1],1/scales_array[mapvalue-1],(10,len(shapes_array[mapvalue-1]))).T+minround
    round_binaries=np.random.binomial(1,winroundprobs,(len(winroundprobs),9))
    round_totals_blu=np.cumsum(round_binaries,axis=1)
    round_totals_red=np.cumsum(1-round_binaries,axis=1)
    cumdurs=np.cumsum(durations,axis=1)
    blu_score=[]
    red_score=[]
    blu_score_half1=[]
    red_score_half1=[]
    blu_score_half2=[]
    red_score_half2=[]
    for i in range(len(round_binaries)):
        red_rounds=0
        blu_rounds=0
        cumdur=durations[i][0]
        j=0
        while (cumdur<1800)&(blu_rounds<3)&(red_rounds<3):
            cumdur+=durations[i][j+1]+5
            blu_rounds=round_totals_blu[i][j]
            red_rounds=round_totals_red[i][j]
            j+=1
        cumdur_1sthalf=cumdur
        blu_score_half1.append(blu_rounds)
        red_score_half1.append(red_rounds)
        blu_rounds_half1=blu_rounds
        red_rounds_half1=red_rounds
        while(cumdur<min(1800+cumdur_1sthalf,3600))&(blu_rounds<5)&(red_rounds<5):
            cumdur+=durations[i][j+1]+5
            blu_rounds=round_totals_blu[i][j]
            red_rounds=round_totals_red[i][j]
            j+=1
        blu_score_half2.append(blu_rounds-blu_rounds_half1)
        red_score_half2.append(red_rounds-red_rounds_half1)
        if blu_rounds==red_rounds:
            blu_rounds=round_totals_blu[i][j]
            red_rounds=round_totals_red[i][j]
        blu_score.append(blu_rounds)
        red_score.append(red_rounds)
    blu_score=np.array(blu_score)
    red_score=np.array(red_score)
    winperc=100*len(blu_score[blu_score>red_score])/len(blu_score)
    plt.figure()
    plt.hist2d(blu_score,red_score,cmap='Greys',bins=np.linspace(-0.5,5.5,7),density=True)
    plt.colorbar(label='Probability');
    plt.xlabel(team_a+' rounds')
    plt.ylabel(team_b+' rounds')
    plt.title(team_a+' has a %3.1f'%winperc+'% chance of winning');
    plt.show()
    return(0)

def predict_rounds_koth(scores,team_a,team_b,rounds_data):
    """
    Big Uncommented function for plotting match predictions for koth maps.
    This doesn't work very well, maybe I'll clean this up in future.
    """
    teamslist=rounds_data.blu_team.unique()
    team_a_score=scores[:,teamslist==team_a]
    team_b_score=scores[:,teamslist==team_b]
    winroundprobs=1/(1+np.exp(team_b_score-team_a_score))
    round_binaries=np.random.binomial(1,winroundprobs,(len(winroundprobs),9))
    round_totals_blu=np.cumsum(round_binaries,axis=1)
    round_totals_red=np.cumsum(1-round_binaries,axis=1)
    blu_score=[]
    red_score=[]
    blu_score_half1=[]
    red_score_half1=[]
    blu_score_half2=[]
    red_score_half2=[]
    for i in range(len(round_binaries)):
        red_rounds=0
        blu_rounds=0
        j=0
        while (blu_rounds<2)&(red_rounds<2):
            blu_rounds=round_totals_blu[i][j]
            red_rounds=round_totals_red[i][j]
            j+=1
        blu_score_half1.append(blu_rounds)
        red_score_half1.append(red_rounds)
        blu_rounds_half1=blu_rounds
        red_rounds_half1=red_rounds
        while(blu_rounds<4)&(red_rounds<4):
            blu_rounds=round_totals_blu[i][j]
            red_rounds=round_totals_red[i][j]
            j+=1
        blu_score.append(blu_rounds)
        red_score.append(red_rounds)
    blu_score=np.array(blu_score)
    red_score=np.array(red_score)
    winperc=100*len(blu_score[blu_score>red_score])/len(blu_score)
    plt.hist2d(blu_score,red_score,cmap='Greys',bins=np.linspace(-0.5,5.5,7),density=True)
    plt.colorbar(label='Probability');
    plt.xlabel(team_a+' rounds')
    plt.ylabel(team_b+' rounds')
    plt.title(team_a+' has a %3.1f'%winperc+'% chance of winning');
    plt.show()
    return(0)


round_durs = pickle.load(open('round_durs.pkl', 'rb'))
team_scores=pickle.load(open('team_scores.pkl', 'rb'))

print('Give name of file (not including file extension) to read in')
filename=input()

#Read in rounds data file
rounds_data=pd.read_csv(filename+'.csv')

#Make a dictionary of the team names and assign a numeric value to each team
numbers=dict(np.flip(np.array(list(enumerate(rounds_data.blu_team.unique()))),axis=1))

#Get the numeric value associated with each team for each round
blunumbers=[]
rednumbers=[]
for blukey in rounds_data.blu_team.values:
    blunumbers.append(numbers[blukey])
for redkey in rounds_data.red_team.values:
    rednumbers.append(numbers[redkey])

#Do the same thing, but for maps
mapnumbers=[]
mindurations=[]
rounds_data_truncated=rounds_data[(rounds_data['round_duration']>40)&(rounds_data['map']!='product')&(rounds_data['map']!='clearcut')] #get rid of process and clearcut (duration doesn't matter)
#also gets rid of any rounds shorter than 40s (normally erroneous)
numbers_map=dict(np.flip(np.array(list(enumerate(rounds_data_truncated.map.unique()))),axis=1)) #get map number values

#grab the MINIMUM durations for each round in our model
for mapkey in rounds_data_truncated.map.values:
    mindurations.append(min(rounds_data_truncated[rounds_data_truncated['map']==mapkey]['round_duration']))
    mapnumbers.append(numbers_map[mapkey])


#Go from python style indexing to C++ style indexing, this is kind of a dumb way of doing it but whatever
rednumbers=pd.Series(np.array(rednumbers)).astype(int).values+1
blunumbers=pd.Series(np.array(blunumbers)).astype(int).values+1
mapnumbers=pd.Series(np.array(mapnumbers)).astype(int).values+1

#Get who won each round
roundscores=rounds_data.blu_win.astype(int).values

#Get durations MINUS the minimum duration
durations=rounds_data_truncated.round_duration.astype(float).values-mindurations

#Try and get the scores for each team:
fit_scores=team_scores.sampling(
    data={'N':len(rednumbers),'M':len(numbers),'roundscores':roundscores,'bluteamnumber':blunumbers,'redteamnumber':rednumbers},
    iter=10000,
    chains=2
)

#Prepare arrays for the shapes and scales to use later.
shapes_array=[]
scales_array=[]

#Work out the distribution of round durations for each map (doesn't really matter much)
for i in np.unique(mapnumbers):
    durations_map=durations[mapnumbers==i]
    fit_map=round_durs.sampling(
        data={'N_data':len(durations_map),'durations':durations_map},
        iter=10000,
        chains=4
    )
    shapes_array.append(fit_map['shape'])
    scales_array.append(fit_map['rate'])

#Adjust scores to specify mean=0
scores=fit_scores['team_scores'].T-np.mean(fit_scores['team_scores'],axis=1)
scores=scores.T

#Shape manipulation for plotting
scoreargs=np.argsort(np.mean(scores,axis=0))
flattenedscores=scores[:,scoreargs].flatten()
flattenedscores.shape
n_teams=fit_scores['team_scores'].shape[1]
flattenedteamnumbers=np.repeat([np.arange(n_teams)],len(fit_scores['team_scores']),axis=0).flatten()

#Plot Image
sns.boxplot(x=flattenedteamnumbers,y=flattenedscores,fliersize=0)
plt.xticks(np.arange(n_teams),rounds_data.blu_team.unique()[scoreargs],rotation=90);
plt.ylabel('Team Score');
plt.show();

print('Do Match Prediction? Type y for yes, anything else to quit')
choice=input()
if choice=='y':
    print('Specify name of first team (Case sensitive, check ranking image)')
    team_a=input()
    print('Specify name of second team (Case sensitive, check ranking image)')
    team_b=input()
    print('Specify name of map (lowercase, no prefix or suffix)')
    name_map=input()
    if name_map in ['clearcut','product']:
        predict_rounds_koth(scores,team_a,team_b,rounds_data)
    else:
        predict_rounds(name_map,scores,team_a,team_b,rounds_data)
quit()
