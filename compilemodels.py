from pystan import StanModel
import pickle
print('This script will compile the statistical models to be used later. It may take a few minutes to complete')
#Stan Model for round durations these models can be edited with some knowledge of the stan probabilistic programming language
round_durations_code="""
data {
    int<lower=0> N_data;
    vector[N_data] durations;
    }
parameters {
    real<lower=1,upper=10> shape;
    real<lower=1./3600,upper=3600> rate;
    }
model {
    durations ~ gamma(shape,rate);
    }
"""
#Stan Model for team scores
team_scores_code="""
  data {
    int<lower=0> N;
    int<lower=0> M;
    int roundscores[N];
    int bluteamnumber[N];
    int redteamnumber[N];
  }
  parameters {
    vector[M] team_scores;
    real<lower=1e-12> sd_teams;

  }
  transformed parameters {
    vector[N] score_diff= team_scores[bluteamnumber]-team_scores[redteamnumber];
  }
  model{
    team_scores~ normal(0,sd_teams);
    roundscores ~ bernoulli_logit(score_diff);
  }
"""
round_durs=StanModel(model_code=round_durations_code)
team_scores=StanModel(model_code=team_scores_code)

#Save Models as pickle file
with open('round_durs.pkl', 'wb') as f:
    pickle.dump(round_durs, f)

with open('team_scores.pkl', 'wb') as f:
    pickle.dump(team_scores, f)

print('Models Compiled, Quitting')
quit()
