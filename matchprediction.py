import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import numpy.random as random
import pystan as stan
import pickle
def predict_rounds(mapname,scores,team_a,team_b,lambdas):
    """
    Big Uncommented function for plotting match predictions.
    This doesn't work very well, maybe I'll clean this up in future.
    """
    team_a_score=scores[team_a].values
    team_b_score=scores[team_b].values
    winroundprobs=1/(1+np.exp(team_b_score-team_a_score))
    maplambda=lambdas[mapname]
    rounds=random.poisson(maplambda,len(winroundprobs))
    rounds2=random.poisson(maplambda,len(winroundprobs))
    round_binaries=np.random.binomial(1,winroundprobs,(9,len(winroundprobs))).T
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
        while (j<=rounds[i])&(blu_rounds<3)&(red_rounds<3):
            blu_rounds=round_totals_blu[i][j]
            red_rounds=round_totals_red[i][j]
            j+=1
        blu_score_half1.append(blu_rounds)
        red_score_half1.append(red_rounds)
        blu_rounds_half1=blu_rounds
        red_rounds_half1=red_rounds
        j=0
        while(j<=rounds2[i])&(blu_rounds<5)&(red_rounds<5):
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
    return(0);

def predict_rounds_koth(scores,team_a,team_b,rounds_data):
    """
    Big Uncommented function for plotting match predictions for koth maps.
    This doesn't work very well, maybe I'll clean this up in future.
    """
    team_a_score=scores[team_a]
    team_b_score=scores[team_b]
    winroundprobs=1/(1+np.exp(team_b_score-team_a_score))

    round_binaries=np.random.binomial(1,winroundprobs,(9,len(winroundprobs))).T
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
        red_score_half1.append
        (red_rounds)
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

    plt.hist2d(blu_score,red_score,cmap='Greys',bins=np.linspace(-0.5,4.5,6),density=True)
    plt.colorbar(label='Probability');
    plt.xlabel(team_a+' rounds')
    plt.ylabel(team_b+' rounds')
    plt.title(team_a+' has a %3.1f'%winperc+'% chance of winning');
    plt.show();
    return(0);

def create_map_data(data):
    """
    Creates a range of possible data.
    """
    model_poisson = pickle.load(open('model_poisson.pkl', 'rb'))
    rounds_data={}
    for mapname in data.map.unique():
        if mapname not in ['clearcut','product']:
            data_map=data[data.map==mapname]
            n_rounds=[]
            durations=[]
            for logid in data_map.log_id.unique():
                log=data_map[data_map.log_id==logid]
                logduration=log.total_duration.unique()[0]
                durations.append(logduration)
                n_rounds.append(len(log))
            durations=np.array(durations)
            n_rounds=np.array(n_rounds)
            fit=model_poisson.sampling({'N':len(n_rounds),'durations':durations,'n_rounds':n_rounds},iter=10000,chains=4)
            rounds_data[mapname]=fit['lambda']
    return(rounds_data)
print('Enter name of data, no filename')
fname=input()
datafile=pd.read_csv(fname+'.csv')
scores=pd.read_csv(fname+'_ranks.csv')
print('Enter first team name, case sensitive, see ranks plot for more info')
team_a=input()
print('Enter second team name, case sensitive, see ranks plot for more info')
team_b=input()
print('Enter map name, lowercase, no suffix or prefix')
mapname=input()
rounds_data=create_map_data(datafile)
if mapname not in ['clearcut','product']:
    predict_rounds(mapname,scores,team_a,team_b,rounds_data)
else:
    predict_rounds_koth(scores,team_a,team_b,rounds_data)
quit()
