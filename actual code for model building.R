# Load Data ---------------------------------------------------------------

pacman::p_load(data.table, finalfit,psych,dplyr,ggplot2,extrafont,
               MASS,ggiraph,lmerTest,tidyverse,performance,stats,tidyr,
               lubridate,dtplyr,binaryLogic,numDeriv,RCurl,reshape2,
               RColorBrewer,afex,scales)

Data <- fread(file.choose())


# filter players ----------------------------------------------------------

Data3 <- Data[,NROW(.SD),playerId]
Data3 <- Data3[V1>10,,]
Data3 <- Data3[V1<100,,]
UNQ <- Data3$playerId
Data <- Data[playerId%in%UNQ,,]


# build model -------------------------------------------------------------

model.building <- function(data=.,wbehavior,alpha,T0){
  col.names <-c('createdAt',paste0('watched_',wbehavior,'_binary')) 
  data <- as.data.table(data)
  data <- data[,col.names,with=FALSE]
  #data <-data[order(createdAt,decreasing = F)]
  #initial row
  try <- data[1, x := .(T0)]
  if(NROW(data)==1){
  }
  else {
    #subsequent rows
    for (nn in 2:nrow(try)){
      new_p <- try[nn - 1L,x]
      try[nn, x := .(new_p+ alpha * (try[nn - 1L,2]-new_p))]
    }
  }
  return(try$x)
}


# sort data ---------------------------------------------------------------

Data <- Data[order(createdAt),.SD,by=playerId]


# build the executing model -----------------------------------------------

execut_model_simple <- function(data=.,alpha,T0){
#revives 0.1
Data2 <- data[,.(playerId,createdAt,watched_revives_binary)]
Data3 <- Data2[,model.building(.SD,'revives',alpha,T0),by=playerId]
data <- data[,paste0('p_revives_',alpha,'_',T0):=Data3$V1,]
gc()

#assists 0.1
Data2 <- data[,.(playerId,createdAt,watched_assists_binary)]
Data3 <- Data2[,model.building(.SD,'assists',alpha,T0),by=playerId]
data <- data[,paste0('p_assists_',alpha,'_',T0):=Data3$V1,]
gc()

#teamKills 0.1
Data2 <- data[,.(playerId,createdAt,watched_teamKills_binary)]
Data3 <- Data2[,model.building(.SD,'teamKills',alpha,T0),by=playerId]
data <- data[,paste0('p_teamKills_',alpha,'_',T0):=Data3$V1,]
gc()
return(data)
}


# Converting to BINARY ----------------------------------------------------

Data$revives_binary <- ifelse(Data$revives==0,0,1)
Data$assists_binary <- ifelse(Data$assists==0,0,1)
Data$teamKills_binary <- ifelse(Data$teamKills==0,0,1)
Data$watched_revives_binary <- ifelse(Data$watched_revives==0,0,1)
Data$watched_assists_binary <- ifelse(Data$watched_assists==0,0,1)
Data$watched_teamKills_binary <- ifelse(Data$watched_teamKills==0,0,1)


# check -------------------------------------------------------------------

Data2 <- Data[playerId=="account.01543729d53049faa2a635fcd4241c45",,]
Data3 <- Data2[,model.building(.SD,'revives',0.1,2),by=playerId]
Data2$check1 <- Data3$V1 
Data2$check2 <- Data3$V1

Data4 <- Data2

Data5 <- execut_model_simple(Data4,0.1,2)


# let's go ----------------------------------------------------------------

Data <- execut_model_simple(Data,alpha = 0.05,T0 = 0.5)
Data <- execut_model_simple(Data,alpha = 0.1,T0 = 0.5)
Data <- execut_model_simple(Data,alpha = 0.5,T0 = 0.5)
Data <- execut_model_simple(Data,alpha = 0.8,T0 = 0.5)
Data <- execut_model_simple(Data,alpha = 0.05,T0 = 0)
Data <- execut_model_simple(Data,alpha = 0.1,T0 = 0)
Data <- execut_model_simple(Data,alpha = 0.5,T0 = 0)
Data <- execut_model_simple(Data,alpha = 0.8,T0 = 0)
Data <- execut_model_simple(Data,alpha = 0.05,T0 = 1)
Data <- execut_model_simple(Data,alpha = 0.1,T0 = 1)
Data <- execut_model_simple(Data,alpha = 0.5,T0 = 1)
Data <- execut_model_simple(Data,alpha = 0.8,T0 = 1)


fwrite(Data,"D:/Ron/WORKS/Thesis/16.12.20/half_way_through1.csv")


# create  game number -----------------------------------------------------
Data[,game_no:=row.names(.SD),playerId]
Data$game_no <- as.numeric(Data$game_no)
# model for LMER ----------------------------------------------------------
## Model with Revives as fixed

#Fixed effects: intercept  + p_revives_0.1_0.5 + p_assists_0.1_0.5

#Random effects: intercept
Data <- fread(file.choose())

Model.revives_0.1_0.5 <- lmer(revives_binary ~ p_revives_0.1_0.5+(1 | playerId),
                              data = Data)
summary(Model.revives_0.1_0.5)
Model.revives_0.1_0.5_timesurvived <- lmer(revives_binary ~ p_revives_0.1_0.5+timeSurvived+(1 | playerId),
                              data = Data)
summary(Model.revives_0.1_0.5_timesurvived)
anova(Model.revives_0.1_0.5,Model.revives_0.1_0.5_timesurvived)


Model.revives_0.1_0.5_timesurvived <- glmer(revives_binary ~ (1 + game_no | playerId) + game_no + mapName + damageDealt + 
                                            timeSurvived + p_assists_0.1_0.5 + p_revives_0.05_0 + heals,
                                            data=Data,family = binomial(link = "logit"))


# lets scale --------------------------------------------------------------
Data1 <- Data
Data1$damageDealt <- scale(Data1$damageDealt)
Data1$timeSurvived <- scale(Data1$timeSurvived)
Data1$p_assists_0.5_1 <- scale(Data1$p_assists_0.5_1)
Data1$p_assists_0.5_0.5 <- scale(Data1$p_assists_0.5_0.5)
Data1$p_assists_0.1_1 <- scale(Data1$p_assists_0.1_1)
Data1$p_revives_0.05_0 <- scale(Data1$p_revives_0.05_0)
Data1$p_revives_0.05_0.5 <- scale(Data1$p_revives_0.05_0)
Data1$p_revives_0.05_1 <- scale(Data1$p_revives_0.05_0)

Data1$p_revives_0.1_0 <- scale(Data1$p_revives_0.1_0)

Data1$heals <- scale(Data1$heals)
Data1$revives_binary <- as.logical(Data1$revives_binary)
Data1$assists_binary <- as.logical(Data1$assists_binary)
Data1$watched_revives_binary <- as.logical(Data1$watched_revives_binary)
Data1$watched_assists_binary <- as.logical(Data1$watched_assists_binary)
Data1$game_no <- as.integer(Data1$game_no)
Data1$assists <- scale(Data1$assists)
Data1$watched_revives <- scale(Data1$watched_revives)
Data1$watched_assists <- scale(Data1$watched_assists)

#Data1$heals <- as.logical(ifelse(Data$heals==0,0,1))
#head(Data1$revives_binary)

Data2 <- Data1
Data2$damageDealt <- scale(Data2$damageDealt)
Data2$timeSurvived <- scale(Data2$timeSurvived)
Data2$p_assists_0.1_0.5 <- scale(Data2$p_assists_0.1_0.5)
Data2$p_revives_0.05_0 <- scale(Data2$p_revives_0.05_0)
# let's go

#empty model
Model <- lmerTest::lmer(revives_binary ~ (1 + game_no || playerId) + 
              game_no + 
              mapName + 
              damageDealt + 
              timeSurvived + 
              p_revives_0.8_1 + 
              heals +
              assists_binary +
              watched_assists_binary +
              watched_revives_binary,
              control = lmerControl(optimizer = "bobyqa"),
              data=Data2)
summary(Model)

ss <- getME(Model,c("theta","fixef"))
m2 <- update(Model,start=ss,control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=2e6)))
summary(m2)
afurl <- "https://raw.githubusercontent.com/lme4/lme4/master/misc/issues/allFit.R"
eval(parse(text=source_https(afurl)))
source_https <- function(url, ...) {
  # load package
  require(RCurl)
  
  # parse and evaluate each .R script
  sapply(c(url, ...), function(u) {
    eval(parse(text = getURL(u, followlocation = TRUE, cainfo = system.file("CurlSSL", "cacert.pem", package = "RCurl"))), envir = .GlobalEnv)
  })
}

# Example
source_https("https://raw.githubusercontent.com/lme4/lme4/master/misc/issues/allFit.R")


Model2 <- update(Model,start=ss)
summary(Model2)
ss2 <- getME(Model2,c("theta","fixef"))
Model3 <- update(Model2,start=ss2)
summary(Model3)
ss3 <- getME(Model3,c("theta","fixef"))
Model4 <- update(Model3,start=ss3)
summary(Model4)
ss4 <- getME(Model4,c("theta","fixef"))
Model5 <- update(Model4,start=ss4)
summary(Model5)


Data2 <- Data1[,list(revives_binary,game_no,playerId, game_no,mapName,damageDealt,timeSurvived, 
                     p_revives_0.8_0,p_revives_0.8_0.5,p_revives_0.8_1,heals,assists_binary,watched_assists_binary,watched_revives_binary)]


Data3 <- fread(file.choose())



ggplot(data = Data3,aes(y=V2))+
  geom_bar()+
  labs(title = "Model's REML comparison")

ggplot(data=Data3, aes(x=V1, y=V2)) + 
  geom_bar( stat='identity') +
  geom_text(aes(label=V2), position=position_dodge(width=0.9), vjust=-0.25)+
  scale_y_continuous(limits=c(537300,537600),oob =rescale_none )+
  theme(axis.text.x = element_text(size = 12,angle = 55, hjust=1,vjust=1),
        axis.title.x = element_text(size=0),
        axis.title.y = element_text(size=14),
        title = element_text(size=18))+
  labs(title = "Model's REML Score Comparison")+
  ylab("REML Score")+
  xlab("")

  
