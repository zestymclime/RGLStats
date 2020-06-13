import pystan
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pickle


team_scores=pickle.load(open('team_scores.pkl', 'rb'))

print('Give name of file (not including file extension) to read in')
filename=input()

#Read in rounds data file
rounds_data=pd.read_csv(filename+'.csv')

#Make a dictionary of the team names and assign a numeric value to each team
teams=np.union1d(rounds_data.blu_team.unique(),rounds_data.red_team.unique())
numbers=dict(np.flip(np.array(list(enumerate(teams))),axis=1))

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
    chains=4
)
#Work out the distribution of round durations for each map (doesn't really matter much)
#Adjust scores to specify mean=0
scores=fit_scores['team_scores'].T-np.mean(fit_scores['team_scores'],axis=1)
scores=scores.T

#Shape manipulation for plotting
scoreargs=np.flip(np.argsort(np.mean(scores,axis=0)))
flattenedscores=scores[:,scoreargs].flatten()
flattenedscores.shape
n_teams=fit_scores['team_scores'].shape[1]
flattenedteamnumbers=np.repeat([np.arange(n_teams)],len(fit_scores['team_scores']),axis=0).flatten()

#Plot Image
sns.boxplot(x=flattenedteamnumbers,y=flattenedscores,fliersize=0)
plt.xticks(np.arange(n_teams),teams[scoreargs],rotation=90);
plt.ylabel('Team Score');
plt.tight_layout();
plt.show();

print('Save ranks for match prediction? Type y for yes, anything else to quit')
choice=input()
if choice=='y':
    rankdf=pd.DataFrame(scores,columns=teams)
    rankdf.to_csv(filename+'_ranks.csv',index=False)
quit()
