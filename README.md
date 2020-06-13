## RGL Scrim/Match Logs Grabber and Team Stats/ Match Prediction Script
#### Updated by Zesty 2020/05/18
- Checks playerids for each team from RGL.gg and grabs scrim and match logs for each player using the logs.tf API
- Can rank teams against one another
- Can do rudimentary match prediction (the code for this is spaghetti code)

### Usage
- Everything Needs Python 3, I recommend downloading Anaconda Python. https://www.anaconda.com/

### Scrim/Match Log Grabbing
- Requires the python packages `pandas`, `numpy`, `time`, `BeautifulSoup`, `cfscrape` and `requests`, + any dependencies these packages may have.
- Run `grablogs.py` from your terminal
- Can get a series of match and scrim logs for a given division. When prompted, input the name of the division you're interested in getting rankings from.
- You need to specify a "start log" which is the log the script will run from (with a suggestion for this season given by prompt). It's also currently limited to 1000 logs for any given player, but that can be edited. Note that the stats model we'll talk about in a second treats old logs as just as important as new logs, so including last season's data might lead to some misleading results if teams have improved!

### Compiling Statistical Models
- Requires the python packages `pystan` and `pickle` + any dependencies these packages might have
- Run `compilemodels.py`
- This compiles the stan models https://mc-stan.org that the statistical model will use later. It should take at most a couple of minutes.
- Stan is distributed under a BSD 3 clause license https://opensource.org/licenses/BSD-3-Clause so I guess this is too.

### Getting Team Ranks
- Requires the python packages `pandas`, `numpy`, `pystan`, `seaborn` and `pickle` + any dependencies.
- Run `teamrankings.py`
- This will prompt you to input the filename for your log csv. You need to have run the log grabbing first, or use the provided InviteData file.
- The first image produced will be ranks for each team. The distance between teams reflects the probability of a team winning a round. The probability of team a winning a round against team b is 1/(1+exp(b-a))
- Likely at an early stage in the season some of these values might be a bit unstable. You can check the rhat statistic by printing the line pystan.check_hmc_diagnostics(fit_scores) into. If this is >1.1 or <0.9 for the team scores, the model likely isn't very good. You can also try running for more iterations if this is a problem. The scores become more precise as more scrims/matches are played, but not necessarily more accurate, e.g. if teams suddenly improve in the latter half of the season.
- Press y to save team ranks if you want to do match prediction.

### Predicting matches
- Run `matchprediction.py`
- You can also run a simulation where team a plays team b on a given map and get the distribution of possible outcomes. This is where the model breaks down a bit, it tends to always think games go to winlimit because most rounds recorded on logs are short. Also this is where the code is just spaghetti code so I need to improve this.



See post https://www.teamfortress.tv/54662/rgl-advanced-s2-happenings-discussion/?page=5#125 for an example of usage and some more detailing. I might update the readme with more documentation if I get the time.

hmu on steam if you have more questions
https://steamcommunity.com/id/mclime
