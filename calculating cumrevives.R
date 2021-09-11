# packages ----------------------------------------------------------------


library(data.table)
library(dplyr)
library(tidyr)
library(psych)


# load data ---------------------------------------------------------------


#read data
Data <- fread(file.choose())

#select relevant data
Data <- select(Data,c(playerId,rosterId,createdAt,revives,assists,teamKills,gameMode))

#filter missing roster data
Data <-Data %>% 
  filter(rosterId!="")

#create team variables, notice group
Data <- Data %>% 
  group_by(rosterId) %>% 
  mutate(teamRevives=sum(revives)) %>% 
  mutate(groupkills=sum(teamKills)) %>% 
  mutate(teamassists=sum(assists))

#filter players that show up once
Data<- Data %>% 
  group_by(playerId) %>% 
  mutate(count=row_number()) %>% 
  mutate(countMax=max(count)) 
Data <- Data %>% 
  filter(countMax!=1)

#filter solo games
Data <- Data %>% 
  filter(gameMode!="solo") %>% 
  filter(gameMode!="solo-fpp") %>% 
  filter(gameMode!="lab-fpp") 


# for revives -------------------------------------------------------------


#create cumulative of revives
singalrevives <- Data %>%
  select(playerId, createdAt, revives,teamRevives) %>%
  group_by (playerId,createdAt) %>%
  summarise(revives=sum(revives)) %>%
  #mutate(CumRevives=cumsum(revives)) %>%
  #mutate(totalRevives = sum(revives)) %>%
  mutate(DidRevives = cumsum(revives)-revives)
teamrevives <- Data %>%
  select(playerId, createdAt, revives,teamRevives) %>%
  group_by (playerId,createdAt) %>%
  summarise(teamRevives=sum(teamRevives)) %>%
  #mutate(CumteamRevives=cumsum(teamRevives)) %>%
  mutate(count=row_number()) %>% 
  mutate(totalteamRevives = sum(teamRevives)) %>%
  mutate(DidteamRevives = cumsum(teamRevives)-teamRevives) %>% 
  mutate(fixedRevives = DidteamRevives/(count-1))

teamrevives$fixedRevives[is.nan(teamrevives$fixedRevives)] <- 0
#for real try$temp <- as.numeric(try$temp)


#merge into one table for correlations
stats_revives <- merge(singalrevives, teamrevives, by = c("playerId","createdAt"))
remove(singalrevives)
remove(teamrevives)

#filter those who never experienced revives within the team
stats_revives <- stats_revives %>%
  filter(totalteamRevives!=0)

#check correlation for team exp and singal exp
corr.test(stats_revives$DidteamRevives,stats_revives$revives,method = "spearman")
corr.test(stats_revives$DidRevives,stats_revives$revives)

#plot
ggplot(data = stats_revives, mapping = aes(x = fixedRevives, y = revives)) + 
  geom_jitter(alpha = 0.1)

# teamkills ---------------------------------------------------------------


#create cumulative of teamkills
singalteamkills <- Data %>%
  select(playerId, createdAt, teamKills,groupkills) %>%
  group_by (playerId,createdAt) %>%
  summarise(teamKills=sum(teamKills)) %>%
  mutate(CumteamKills=cumsum(teamKills)) %>%
  mutate(totalteamKills = sum(teamKills)) %>%
  mutate(DidteamKills = CumteamKills-teamKills)
groupteamkills <- Data %>%
  select(playerId, createdAt, teamKills,groupkills) %>%
  group_by (playerId,createdAt) %>%
  summarise(groupkills=sum(groupkills)) %>%
  mutate(Cumgroupkills=cumsum(groupkills)) %>%
  mutate(totalgroupkills = sum(groupkills)) %>%
  mutate(Didgroupkills = Cumgroupkills-groupkills)

#merge into one table for correlations
stats_teamkills <- merge(singalteamkills, groupteamkills, by = c("playerId","createdAt"))
remove(singalteamkills)
remove(groupteamkills)

#filter those who never experienced teamkills within the team
stats_teamkills <- stats_teamkills %>%
  filter(totalgroupkills!=0)

#check correlation for team exp and singal exp
corr.test(stats_teamkills$Didgroupkills,stats_teamkills$teamKills)
corr.test(stats_teamkills$DidteamKills,stats_teamkills$teamKills)

#plot
plot(stats_teamkills$Didgroupkills,stats_teamkills$teamKills)


# assists -----------------------------------------------------------------


#create cumulative of assists
singalassists <- Data %>%
  select(playerId, createdAt, assists,teamassists) %>%
  group_by (playerId,createdAt) %>%
  summarise(assists=sum(assists)) %>%
  mutate(Cumassists=cumsum(assists)) %>%
  mutate(totalassists = sum(assists)) %>%
  mutate(Didassists = Cumassists-assists)
teamassists <- Data %>%
  select(playerId, createdAt, assists,teamassists) %>%
  group_by (playerId,createdAt) %>%
  summarise(teamassists=sum(teamassists)) %>%
  mutate(Cumteamassists=cumsum(teamassists)) %>%
  mutate(totalteamassists = sum(teamassists)) %>%
  mutate(Didteamassists = Cumteamassists-teamassists)

#merge into one table for correlations
stats_assists <- merge(singalassists, teamassists, by = c("playerId","createdAt"))
remove(singalassists)
remove(teamassists)

#filter those who never experienced assists within the team
stats_assists <- stats_assists %>%
  filter(totalteamassists!=0)

#check correlation for team exp and singal exp
corr.test(stats_assists$Didteamassists,stats_assists$assists)
corr.test(stats_assists$Didassists,stats_assists$assists)

#plot
plot(stats_assists$Didteamassists,stats_assists$assists)

