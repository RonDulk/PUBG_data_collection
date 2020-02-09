library(dplyr)
library(parameters) # for kurtosis & skewness
library(summarytools)
library(ggplot2)
clean <-  read.csv("matches.csv")
glimpse(clean)
clean1 <- filter(clean,
                 teamId >0)
glimpse(clean1)
clean1 <- filter(clean1,
                 teamId <150)
glimpse(clean1)
write.csv(clean1,file="Clean.csv")
ggplot(clean1, aes(x = rank, y = revives)) +
       geom_point() +
       geom_smooth(method="lm")
ggplot(clean1, aes(x = rank, y = revives)) +
  geom_point() +
  geom_smooth()
ggplot(clean1, aes(x = rank, y = revives)) +
  geom_point() +
  geom_smooth(method="lm")+
  facet_grid( ~ gameMode)
ggplot(clean1, aes(x = rank, y = revives)) +
  geom_point() +
  geom_smooth() +
  facet_grid( ~ gameMode)
