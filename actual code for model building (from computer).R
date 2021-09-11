# Load Data ---------------------------------------------------------------

pacman::p_load(data.table, finalfit,psych,dplyr,ggplot2,extrafont,
               MASS,ggiraph,lmerTest,tidyverse,performance,stats,tidyr,
               lubridate,dtplyr,binaryLogic,numDeriv,RCurl,reshape2,
               RColorBrewer,afex)

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
Data1$p_revives_0.1_0 <- scale(Data1$p_revives_0.1_0)

Data1$heals <- scale(Data1$heals)
Data1$revives_binary <- as.logical(Data1$revives_binary)
Data1$assists_binary <- as.logical(Data1$assists_binary)
Data1$watched_assists_binary <- as.logical(Data1$watched_assists_binary)
Data1$watched_revives_binary <- as.logical(Data1$watched_revives_binary)

#ata1$game_no <- as.integer(Data1$game_no)
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
Model <- lmer(revives_binary ~ (1 + game_no | playerId) + 
              game_no + 
              mapName + 
              damageDealt + 
              timeSurvived + 
           #   p_assists_0.1_1 + 
              p_revives_0.05_0 + 
              heals +
              assists_binary +
              watched_assists_binary +
              watched_revives_binary,
              control = lmerControl(optimizer = "bobyqa",optCtrl=list(maxfun=2e6)),
              data=Data1)
summary(Model)

ss <- getME(Model,c("theta","fixef"))
m2 <- update(Model,start=ss,control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=2e6)))
summary(m2)

#Descriptives
Data2 <- Data[,list(game_no,damageDealt,timeSurvived,heals,assists,watched_assists,watched_revives,playerId)]

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

# create graphs
#list of player IDS
player_list <- sample(Data$playerId,25)
Data3 <- Data[playerId%in%player_list]
Data3$revives_binary <- as.logical(Data3$revives_binary) 
p <- ggplot(data=Data3,mapping=aes(x=game_no, y=p_revives_0.05_0)) +
  geom_line(aes(x=game_no, y=p_revives_0.05_0))+
  geom_point(aes(x=game_no, y=p_revives_0.05_0,color=revives_binary),size=1) + 
  scale_color_manual(values = c("FALSE" = "black", "TRUE" = "green"))+
  labs(title="Revives of 25 Random Players \nas a Factor of Their Expectations",x="Game Number",y="Players' Revive Expectations",colour = "Performed \na Revive")+
  theme(plot.title = element_text(family = "Helvetica", face = "bold", size = (16),hjust = 0.5),
        axis.title = element_text(family = "Helvetica", size = (14)),
        legend.title = element_text(family = "Helvetica", size = (14)))
  p + facet_wrap(~playerId, labeller = numbers_labeller)
numbers <- list("account.c02ac08479a74765b8c7c1ca8ce7f0ca"=19,"account.1a0d70f691014241a0648c157d6cac3d"=5,"account.c78338b7f8ff404fa5572056e4d10a2a"=20,
                "account.53fd828f21954b4dbff38accd749fa4a"=9,"account.576ee46ed0844eae962a6280eaf60378"=10,"account.eae26cde015748819ae6353f5612fcd5"=25,
                "account.91ade518f67c4eca8812dbe8a1d3ad5a"=16, "account.1053601c1e214379b24e3d7381bb8be8"=3, "account.23b03d449dd14951bb4b2be20d177041"=6,
                "account.5bd8dc79e29f44bca2f76219adefe2cb"=11, "account.756872b40a764bfe86c16c9e65f80de4"=13, "account.0e063451a3724e2e960f90ae0e7fb851"=2,
                "account.44b1953476304d4db192a65563f071b6"=8, "account.8c6933d13484402c9e3d6c34a62f93e2"=15, "account.d50eeae9b38c4fcda8ded0be2bfa1f51"=21,
                "account.e39783c7f890424e8e46132a26e2c6bd"=23, "account.b6c9dcb4571545c6ad4c543b034d2618"=17, "account.88be944f9111488aa800cd9cef6fb281"=14,
                "account.e32143c633b14ce3bc9f9aec8fa98ebb"=22, "account.eac9e7674e2946098a2a95f026b1076c"=24, "account.195c6ba2c1b44bf8a71ec3a8e70c891c"=4,
                "account.03938a8597f1494e99ba4aa2e013c230"=1, "account.381316017a044247930a7d213ea50647"=7, "account.b92fdfb602b0451c9341a004a092d12c"=18,
                "account.67915d801d2e4c6b8c2cc513650c5118"=12)

numbers_labeller <- function(variable,value){
  return(numbers[value])
}


#exploring random effect with plot
ranef_subj <- ranef(Model)$playerId
ranef_subj_intercepts <- ranef_subj$`(Intercept)`
ranef_subj_slopes <- ranef_subj$game_no
cor(ranef_subj_intercepts, ranef_subj_slopes)


ggplot(mapping=aes(x=ranef_subj_intercepts, y=ranef_subj_slopes)) +
  geom_point(aes(x=ranef_subj_intercepts, y=ranef_subj_slopes),size=1) + 
  scale_y_continuous(breaks=seq(-0.0015,0.001,0.0005))+
  labs(title="Players' Random Effect of Game Number",x="Players' intercepts",y="Game Number Slopes")+
  theme(plot.title = element_text(family = "Helvetica", face = "bold", size = (16),hjust = 0.5),
        axis.title = element_text(family = "Helvetica", size = (14)),
        legend.title = element_text(family = "Helvetica", size = (14)))

#now fixed effect
Data4 <- Data[,list(revives,revives_binary,game_no)]
Data4 <- Data4[,c(.(proportion=sum(revives_binary)/.N),N=.N),by=game_no]


ggplot(data=Data4[game_no<98],mapping=aes(x=game_no, y=proportion)) +
  geom_point(aes(x=game_no, y=proportion,size=N))+
  labs(title="Proportion of Players That Revived by Game Number",x="Players' Game Number",y="Percentage of Players That Revived",size="N (Players)")+
  theme(plot.title = element_text(family = "Helvetica", face = "bold", size = (16),hjust = 0.5),
        axis.title = element_text(family = "Helvetica", size = (14)),
        legend.title = element_text(family = "Helvetica", size = (14)))

ggplot(data=Data,mapping=aes(x=game_no, y=revives_binary)) +
  geom_smooth(method = "lm")+
  geom_count(aes(x=game_no, y=revives_binary))+
  labs(title="Players' Fixed Effect of Game Number",x="Players' Game",y="Did Revive")+
  theme(plot.title = element_text(family = "Helvetica", face = "bold", size = (16),hjust = 0.5),
        axis.title = element_text(family = "Helvetica", size = (14)),
        legend.title = element_text(family = "Helvetica", size = (14)))




# proportion for each expectation -----------------------------------------

# of all players
Data6 <- Data[,list(playerId,p_revives_0.05_0,revives_binary)]
Data6 <- Data6[,new_p:=trunc(p_revives_0.05_0/0.05)*0.05]
Data6 <- Data6[,new_p:=paste0(new_p,"-",new_p+0.05)]
Data6 <- Data6[,c(.(proportion=sum(revives_binary)/.N),N=.N),by=new_p]

ggplot(data=Data6,mapping=aes(x=new_p, y=proportion)) +
  geom_point(aes(x=new_p, y=proportion,size=N))+
  labs(title="Proportion of Plyaers Reviving by Expectations",x="Players' Expectation",y="Percentage of Revives per Expectation",size="N (Players)")+
  theme(plot.title = element_text(family = "Helvetica", face = "bold", size = (16),hjust = 0.5),
        axis.title = element_text(family = "Helvetica", size = (14)),
        legend.title = element_text(family = "Helvetica", size = (14)))


# comparing two dates -----------------------------------------------------

Data <- fread(file.choose(), select = c("playerId","createdAt","revives"))
Data$revives <- ifelse(Data$revives==0,0,1)
Data <- Data[,createdAt:=as.Date(createdAt,format="%Y-%m-%d")]
Data <- Data[,.(proportion=sum(revives)/.N),by=createdAt]
Data$createdAt <- as.factor(Data$createdAt)
Data <- Data[,createdAt:=format(as.Date(createdAt,format="%Y-%m-%d"),format="%d-%m")]
Data$createdAt <- as.factor(Data$createdAt)


ggplot(data=Data,mapping=aes(x=createdAt, y=proportion)) +
  geom_bar(aes(x=createdAt, y=proportion),stat = "identity")+
  labs(title="Proportion of Plyaers Reviving by Date in 2021",x="Date of Game",y="Percentage of Revives per Day")+
  theme(plot.title = element_text(family = "Helvetica", face = "bold", size = (16),hjust = 0.5),
        axis.title = element_text(family = "Helvetica", size = (14)),
        legend.title = element_text(family = "Helvetica", size = (14)))

# proportion of expectation by games -----------------------------------------
Data5 <- Data[,list(revives,revives_binary,game_no,p_revives_0.05_0)]

Data5 <- Data5[,c(.(average=sum(p_revives_0.05_0)/.N),N=.N),by=game_no]

ggplot(data=Data5[game_no<98],mapping=aes(x=game_no, y=average)) +
  geom_point(aes(x=game_no, y=average,size=N))+
  labs(title="Players' Average Expectations by Game Number",x="Players' Game Number",y="Average Expectation",size="N (Players)")+
  theme(plot.title = element_text(family = "Helvetica", face = "bold", size = (16),hjust = 0.5),
        axis.title = element_text(family = "Helvetica", size = (14)),
        legend.title = element_text(family = "Helvetica", size = (14)))

# proportion of watched revives by games -----------------------------------------
Data7 <- Data[,list(revives,watched_revives_binary,game_no)]
Data7 <- Data7[,c(.(proportion=sum(watched_revives_binary)/.N),N=.N),by=game_no]


ggplot(data=Data7[game_no<98],mapping=aes(x=game_no, y=proportion)) +
  geom_point(aes(x=game_no, y=proportion,size=N))+
  labs(title="Proportion of Players That Watched Revives by Game Number",x="Players' Game Number",y="Percentage of Watched Revives",size="N (Players)")+
  theme(plot.title = element_text(family = "Helvetica", face = "bold", size = (16),hjust = 0.5),
        axis.title = element_text(family = "Helvetica", size = (14)),
        legend.title = element_text(family = "Helvetica", size = (14)))
