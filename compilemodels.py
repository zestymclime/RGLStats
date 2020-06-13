from pystan import StanModel
import pickle
print('This script will compile the statistical models to be used later. It may take a few minutes to complete')
#Stan Model for round durations these models can be edited with some knowledge of the stan probabilistic programming language
model_poisson_code="""
data {
  int N;
  vector[N] durations;
  int n_rounds[N];
}
parameters{
  real<lower=0,upper=10> lambda;
}
model{
  n_rounds ~ poisson(durations * lambda/1800.);
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
round_durs=StanModel(model_code=model_poisson_code)
team_scores=StanModel(model_code=team_scores_code)

#Save Models as pickle file
with open('model_poisson.pkl', 'wb') as f:
    pickle.dump(round_durs, f)

with open('team_scores.pkl', 'wb') as f:
    pickle.dump(team_scores, f)

print('Models Compiled, Quitting')
quit()
