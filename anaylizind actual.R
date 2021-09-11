# Load Data ---------------------------------------------------------------

pacman::p_load(data.table, finalfit,psych,dplyr,ggplot2,extrafont,MASS,ggiraph,lmerTest,tidyverse,performance,stats,tidyr,lubridate,dtplyr,gganimate,tweenr)
`%notin%` <- Negate(`%in%`)
Data <- fread(file.choose())
devtools::install_github("thomasp85/transformr")

# devide and aggregate all the data ----------------------------------------------------
Data_all <- Data
Data_all <- Data_all[,fixed_revives:=revives/timeSurvived]
Data_all <- Data_all[, `:=` (revives_means = mean(revives),
                       fixed_revives_means = mean(fixed_revives)), by = c("`name`","`before/after`")]
Data_all <- Data_all[,list(name,`before/after`,revives_means,fixed_revives_means,`positive/negative`)]
Data_all <- distinct(Data_all)
Data_all <- Data_all[`before/after`!="",]
Data_all <- Data_all[`before/after`!="game",]
Data_all <- dcast(Data_all,name+`positive/negative`~`before/after`,value.var = list("revives_means","fixed_revives_means"))
Data_all <- Data_all[,delta:=revives_means_after-revives_means_before]
Data_all <- Data_all[,fixed_delta:=fixed_revives_means_after-fixed_revives_means_before]
setnames(Data_all, 2, "group")
Data_all_positive <- Data_all[group==2,]
Data_all_neutral <- Data_all[group==1,]
# now only minimal --------------------------------------------------------
Data_minimal <- Data
Data_minimal$timeSurvived <- as.numeric(Data_minimal$timeSurvived)
Data_minimal <- Data_minimal[,fixed_revives:=revives/timeSurvived]
Data_minimal <- Data_minimal[, `:=` (revives_means = mean(revives),
                             fixed_revives_means = mean(fixed_revives)), by = c("`name`","`before/after`")]
Data_minimal <- Data_minimal[,list(name,`before/after`,revives_means,fixed_revives_means,`positive/negative`)]
Data_minimal <- distinct(Data_minimal)
Data_minimal <- Data_minimal[`before/after`!="",]
Data_minimal <- Data_minimal[`before/after`!="game",]
Data_minimal <- dcast(Data_minimal,name+`positive/negative`~`before/after`,value.var = list("revives_means","fixed_revives_means"))
Data_minimal <- Data_minimal[,delta:=revives_means_after-revives_means_before]
Data_minimal <- Data_minimal[,fixed_delta:=fixed_revives_means_after-fixed_revives_means_before]
setnames(Data_minimal, 2, "group")
Data_minimal_positive <- Data_minimal[group==2,]
Data_minimal_neutral <- Data_minimal[group==1,]


# now only up to ten ---------------------------------------------------------------
Data_ten <- Data
Data_ten <- Data_ten[,fixed_revives:=revives/timeSurvived]
Data_ten <- Data_ten[, `:=` (revives_means = mean(revives),
                             fixed_revives_means = mean(fixed_revives)), by = c("`name`","`before/after`")]
Data_ten <- Data_ten[,list(name,`before/after`,revives_means,fixed_revives_means,`positive/negative`)]
Data_ten <- distinct(Data_ten)
Data_ten <- Data_ten[`before/after`!="",]
Data_ten <- Data_ten[`before/after`!="game",]
Data_ten <- dcast(Data_ten,name+`positive/negative`~`before/after`,value.var = list("revives_means","fixed_revives_means"))
Data_ten <- Data_ten[,delta:=revives_means_after-revives_means_before]
Data_ten <- Data_ten[,fixed_delta:=fixed_revives_means_after-fixed_revives_means_before]
setnames(Data_ten, 2, "group")
Data_ten_positive <- Data_ten[group==2,]
Data_ten_neutral <- Data_ten[group==1,]


# now only one ------------------------------------------------------------
Data_one <- Data
Data_one <- Data_one[,fixed_revives:=revives/timeSurvived]
Data_one <- Data_one[, `:=` (revives_means = mean(revives),
                             fixed_revives_means = mean(fixed_revives)), by = c("`name`","`before/after`")]
Data_one <- Data_one[,list(name,`before/after`,revives_means,fixed_revives_means,`positive/negative`)]
Data_one <- distinct(Data_one)
Data_one <- Data_one[`before/after`!="",]
Data_one <- Data_one[`before/after`!="game",]
Data_one <- dcast(Data_one,name+`positive/negative`~`before/after`,value.var = list("revives_means","fixed_revives_means"))
Data_one <- Data_one[,delta:=revives_means_after-revives_means_before]
Data_one <- Data_one[,fixed_delta:=fixed_revives_means_after-fixed_revives_means_before]
setnames(Data_one, 2, "group")
Data_one_positive <- Data_one[group==2,]
Data_one_neutral <- Data_one[group==1,]


# lets draw ---------------------------------------------------------------

Data <- fread(file.choose())
Data_draw <- Data
Data_draw <- Data_draw[`before/after`=="before",try:=.N,by=name]
Data_draw <- Data_draw[,after_max:=max(na.omit(try)),by=name]

Data_draw <- Data_draw %>% 
  as.data.frame() %>% 
  group_by(name) %>% 
  mutate(game_no=row_number()-(after_max+1))
Data_draw <- as.data.table(Data_draw)
Data_draw <- Data_draw[`before/after`!=""]
Data_draw <- Data_draw[,fixed_revives:=revives/timeSurvived]
Data_draw <- Data_draw[game_no<2]
Data_draw <- Data_draw[game_no>-2]
#Data_draw <- Data_draw[fixed_revives>0]

Data_draw1 <- Data_draw[`positive/negative`==1]
Data_draw2 <- Data_draw[`positive/negative`==2]


ggplot(data=Data_draw2,mapping=aes(x=game_no, y=fixed_revives))+
  geom_smooth(method = "lm")+
  geom_line(data=Data_draw2,mapping=aes(x=game_no, y=fixed_revives,group = name,color= name),alpha = 0.3)+
  geom_vline(xintercept = 0, linetype="dotted", color = "blue", size=1.5)+
  theme(legend.position ="none")+
  geom_jitter(mapping=aes(x=game_no, y=fixed_revives,group = name,color= name),width = 0.1,alpha=0.4)+
  scale_x_continuous(breaks = seq(min(Data_draw2$game_no),max(Data_draw2$game_no),1)) + labs(x = "game_no", y = "Revives per round") + 
  theme(text = element_text(color = "white", family = "Bahnschrift"),
        plot.title = element_text(color = "white", family = "Bahnschrift", face = "bold"),
        axis.text = element_text(color = "white", family = "Bahnschrift"),
        panel.background = element_rect(fill = "#212121", color = "#212121"),
        plot.background = element_rect(fill = "#212121", color = "#212121"),
        panel.grid = element_blank(),
        panel.grid.major = element_line(color = "#424242", size = rel(0.5)),
        panel.grid.minor = element_blank())

ggplot(data=Data_draw1,mapping=aes(x=game_no, y=fixed_revives))+
  geom_smooth(method = "lm")+
  geom_line(data=Data_draw1,mapping=aes(x=game_no, y=fixed_revives,group = name,color= name),alpha = 0.3)+
  geom_vline(xintercept = 0, linetype="dotted", color = "blue", size=1.5)+
  theme(legend.position ="none")+
  geom_jitter(mapping=aes(x=game_no, y=fixed_revives,group = name,color= name),width = 0.1,alpha=0.4)+
  scale_x_continuous(breaks = seq(min(Data_draw1$game_no),max(Data_draw1$game_no),1)) + labs(x = "game_no", y = "Revives per round") + 
  theme(text = element_text(color = "white", family = "Bahnschrift"),
        plot.title = element_text(color = "white", family = "Bahnschrift", face = "bold"),
        axis.text = element_text(color = "white", family = "Bahnschrift"),
        panel.background = element_rect(fill = "#212121", color = "#212121"),
        plot.background = element_rect(fill = "#212121", color = "#212121"),
        panel.grid = element_blank(),
        panel.grid.major = element_line(color = "#424242", size = rel(0.5)),
        panel.grid.minor = element_blank())

ggplot(data=Data_draw,mapping=aes(x=game_no, y=fixed_revives))+
  geom_smooth(data=Data_draw1,method = "lm",color="red")+
  geom_smooth(data=Data_draw2,method = "lm",color="blue")+
  geom_line(data=Data_draw,mapping=aes(x=game_no, y=fixed_revives,group = name,color=color),alpha = 0.3)+
  geom_vline(xintercept = 0, linetype="dotted", color = "yellow", size=1.5)+
  theme(legend.position ="none")+
  geom_jitter(mapping=aes(x=game_no, y=fixed_revives,group =color,color=color),width = 0.1,alpha=0.4)+
  scale_x_continuous(breaks = seq(min(Data_draw$game_no),max(Data_draw$game_no),1)) + labs(x = "game_no", y = "Revives per round") + 
  theme(text = element_text(color = "white", family = "Bahnschrift"),
        plot.title = element_text(color = "white", family = "Bahnschrift", face = "bold"),
        axis.text = element_text(color = "white", family = "Bahnschrift"),
        panel.background = element_rect(fill = "#212121", color = "#212121"),
        plot.background = element_rect(fill = "#212121", color = "#212121"),
        panel.grid = element_blank(),
        panel.grid.major = element_line(color = "#424242", size = rel(0.5)),
        panel.grid.minor = element_blank())

Data_draw[,color:=as.character(`positive/negative`)]
Data_draw <- Data_draw[fixed_revives>0]
Data_draw1 <- Data_draw[`positive/negative`==1]
Data_draw2 <- Data_draw[`positive/negative`==2]

ggplot(data=Data_draw,mapping=aes(x=game_no, y=fixed_revives))+
  geom_smooth(data=Data_draw1,method="lm",color="red")+
  geom_smooth(data=Data_draw2,method="lm",color="blue")+
  geom_line(data=Data_draw,mapping=aes(x=game_no, y=fixed_revives,group = name,color=color),alpha = 0.3)+
  geom_vline(xintercept = 0, linetype="dotted", color = "yellow", size=1.5)+
  theme(legend.position ="none")+
  geom_jitter(mapping=aes(x=game_no, y=fixed_revives,group =color,color=color),width = 0.1,alpha=0.4)+
  scale_x_continuous(breaks = seq(min(Data_draw$game_no),max(Data_draw$game_no),1)) + labs(x = "game_no", y = "Revives per round") + 
  theme(text = element_text(color = "white", family = "Bahnschrift"),
        plot.title = element_text(color = "white", family = "Bahnschrift", face = "bold"),
        axis.text = element_text(color = "white", family = "Bahnschrift"),
        panel.background = element_rect(fill = "#212121", color = "#212121"),
        plot.background = element_rect(fill = "#212121", color = "#212121"),
        panel.grid = element_blank(),
        panel.grid.major = element_line(color = "#424242", size = rel(0.5)),
        panel.grid.minor = element_blank())




# trying animate ----------------------------------------------------------
Data_draw <- Data
Data_draw <- Data_draw[`before/after`=="before",try:=.N,by=name]
Data_draw <- Data_draw[,after_max:=max(na.omit(try)),by=name]

Data_draw <- Data_draw %>% 
  as.data.frame() %>% 
  group_by(name) %>% 
  mutate(game_no=row_number()-(after_max+1))
Data_draw <- as.data.table(Data_draw)
Data_draw <- Data_draw[`before/after`!=""]
Data_draw <- Data_draw[,fixed_revives:=revives/timeSurvived]
Data_draw_full <- data.table()
for (i in 2:11) {
  Data_draw_temp <- Data_draw[game_no<i]
  Data_draw_temp <- Data_draw_temp[game_no>-i]
  Data_draw_temp <- Data_draw_temp[,no:=i ]
  Data_draw_full <- rbind(Data_draw_full,Data_draw_temp)
}
Data_draw_full$no <-as.numeric(Data_draw_full$no) 
Data_draw_full[,color:=as.character(`positive/negative`)]
Data_draw_full <- Data_draw_full[fixed_revives>0]

Data_draw_full1 <- Data_draw_full[`positive/negative`==1]
Data_draw_full2 <- Data_draw_full[`positive/negative`==2]

G <- ggplot(data=Data_draw_full,mapping=aes(x=game_no, y=fixed_revives))+
  geom_smooth(data=Data_draw_full1,method="lm",color="red")+
  geom_smooth(data=Data_draw_full2,method="lm",color="green")+
  geom_line(data=Data_draw_full,mapping=aes(x=game_no, y=fixed_revives,group = name,color=color),alpha = 0.3)+
  geom_vline(xintercept = 0, linetype="dotted", color = "yellow", size=1.5)+
  theme(legend.position ="none")+
  geom_jitter(mapping=aes(x=game_no, y=fixed_revives,group =color,color=color),width = 0.1,alpha=0.4)+
  scale_x_continuous(breaks = seq(min(Data_draw_full$game_no),max(Data_draw_full$game_no),1)) + labs(x = "Game Number", y = "Revives per round") + 
  theme(text = element_text(color = "white", family = "Bahnschrift"),
        plot.title = element_text(color = "white", family = "Bahnschrift", face = "bold"),
        axis.text = element_text(color = "white", family = "Bahnschrift"),
        panel.background = element_rect(fill = "#212121", color = "#212121"),
        plot.background = element_rect(fill = "#212121", color = "#212121"),
        panel.grid = element_blank(),
        panel.grid.major = element_line(color = "#424242", size = rel(0.5)),
        panel.grid.minor = element_blank())

animation <- G+transition_time(no) +
  labs(title="Games Before and After:{frame_time-1}") + 
  view_follow(fixed_y = T)  


devtools::install_github('thomasp85/tweenr')
devtools::install_github('thomasp85/transformr')

animate(animation,duration = 20,nframes=10,renderer = gifski_renderer("gganim1.gif"))
animate(animation,duration = 20,nframes=10)




# tests -------------------------------------------------------------------
library("ggpubr")
#for all
#t.test(Data_all_positive$delta,Data_all_neutral$delta,"greater",var.equal = T)
t.test(Data_all_positive$fixed_delta,Data_all_neutral$fixed_delta,"greater",var.equal = T)
ggboxplot(Data_all, x = "group", y = "fixed_delta", 
          color = "group", palette = c("#00AFBB", "#E7B800"),
          ylab = "fixed_delta", xlab = "group")

# for minimal
#t.test(Data_minimal_positive$delta,Data_minimal_neutral$delta,"greater",var.equal = T)
t.test(Data_minimal_positive$fixed_delta,Data_minimal_neutral$fixed_delta,"greater",var.equal = T)
ibrary("ggpubr")
ggboxplot(Data_minimal, x = "group", y = "fixed_delta", 
          color = "group", palette = c("#00AFBB", "#E7B800"),
          ylab = "fixed_delta", xlab = "group")

# for ten
#t.test(Data_ten_positive$delta,Data_ten_neutral$delta,"greater",var.equal = T)
t.test(Data_ten_positive$fixed_delta,Data_ten_neutral$fixed_delta,"greater",var.equal = T)
ibrary("ggpubr")
ggboxplot(Data_ten, x = "group", y = "fixed_delta", 
          color = "group", palette = c("#00AFBB", "#E7B800"),
          ylab = "fixed_delta", xlab = "group")

# for one
#t.test(Data_one_positive$delta,Data_one_neutral$delta,"greater",var.equal = T)
t.test(Data_one_positive$fixed_delta,Data_one_neutral$fixed_delta,"greater",var.equal = T)
ibrary("ggpubr")
ggboxplot(Data_one, x = "group", y = "fixed_delta", 
          color = "group", palette = c("#00AFBB", "#E7B800"),
          ylab = "fixed_delta", xlab = "group")


fwrite(Data_all,"G:/Thesis/experimental phase/actual/Data_all.csv")
fwrite(Data_minimal,"G:/Thesis/experimental phase/actual/Data_minimal.csv")
fwrite(Data_ten,"G:/Thesis/experimental phase/actual/Data_ten.csv")
fwrite(Data_one,"G:/Thesis/experimental phase/actual/Data_one.csv")



# create tables up to ten -------------------------------------------------
for (i in 3:10) {
  

Data_loop <- Data_draw
Data_loop <- as.data.table(Data_loop)
Data_loop <- Data_loop[game_no<i]
Data_loop <- Data_loop[game_no>-i]
Data_loop <- Data_loop[,fixed_revives:=revives/timeSurvived]
Data_loop <- Data_loop[, `:=` (revives_means = mean(revives),
                             fixed_revives_means = mean(fixed_revives)), by = c("`name`","`before/after`")]
Data_loop <- Data_loop[,list(name,`before/after`,revives_means,fixed_revives_means,`positive/negative`)]
Data_loop <- distinct(Data_loop)
Data_loop <- Data_loop[`before/after`!="",]
Data_loop <- Data_loop[`before/after`!="game",]
Data_loop <- dcast(Data_loop,name+`positive/negative`~`before/after`,value.var = list("revives_means","fixed_revives_means"))
Data_loop <- Data_loop[,delta:=revives_means_after-revives_means_before]
Data_loop <- Data_loop[,fixed_delta:=fixed_revives_means_after-fixed_revives_means_before]
fwrite(Data_loop,paste0("G:/Thesis/experimental phase/actual/Data_",i-1,".csv"))
}

t.test(Data_loop[`positive/negative`==2,fixed_delta],Data_loop[`positive/negative`==1,fixed_delta],"greater",var.equal = T)


# let's compute descriptives-------------------------------------------------------------------------
fixed_revives_means <- c()
fixed_revives_means_before <- c()
fixed_revives_means_after <- c()
fixed_revives_std <- c()
fixed_revives_std_before <- c()
fixed_revives_std_after <- c()


for (i in 2:11) {
Data_loop <- Data_draw
Data_loop <- as.data.table(Data_loop)
Data_loop <- Data_loop[game_no<i]
Data_loop <- Data_loop[game_no>-i]
Data_loop <- Data_loop[,fixed_revives:=revives/timeSurvived]
Data_loop <- Data_loop[`before/after`!="",]
fixed_revives_means_before <- c(fixed_revives_means_before,mean(Data_loop[and(`before/after`=="before",`positive/negative`==2),fixed_revives]),
                                                           mean(Data_loop[and(`before/after`=="before",`positive/negative`==1),fixed_revives]))
fixed_revives_means_after <- c(fixed_revives_means_after,mean(Data_loop[and(`before/after`=="after",`positive/negative`==2),fixed_revives]),
                                                         mean(Data_loop[and(`before/after`=="after",`positive/negative`==1),fixed_revives]))
fixed_revives_std_before <- c(fixed_revives_std_before,sd(Data_loop[and(`before/after`=="before",`positive/negative`==2),fixed_revives]),
                                                       sd(Data_loop[and(`before/after`=="before",`positive/negative`==1),fixed_revives]))
fixed_revives_std_after <- c(fixed_revives_std_after,sd(Data_loop[and(`before/after`=="after",`positive/negative`==2),fixed_revives]),
                                                     sd(Data_loop[and(`before/after`=="after",`positive/negative`==1),fixed_revives]))
}
Data_Descriptives <- data.table(c(paste0(c("positive game number","neutral game number"),rep(1:10, each=2))))
Data_Descriptives <- Data_Descriptives[,fixed_revives_means_before:=fixed_revives_means_before]
Data_Descriptives <- Data_Descriptives[,fixed_revives_means_after:=fixed_revives_means_after]
Data_Descriptives <- Data_Descriptives[,fixed_revives_std_before:=fixed_revives_std_before]
Data_Descriptives <- Data_Descriptives[,fixed_revives_std_after:=fixed_revives_std_after]



# prepating LMM --------------------------------------------------------------

Data_lmer <- Data
Data_lmer <- Data_lmer[`before/after`=="before",try:=.N,by=name]
Data_lmer <- Data_lmer[,after_max:=max(na.omit(try)),by=name]

Data_lmer <- Data_lmer %>% 
  as.data.frame() %>% 
  group_by(name) %>% 
  mutate(game_no=row_number()-(after_max+1))
Data_lmer <- as.data.table(Data_lmer)
Data_lmer <- Data_lmer[`before/after`!=""]
Data_lmer <- Data_lmer[`before/after`!="game"]
Data_lmer$`positive/negative` <- as.character(Data_lmer$`positive/negative`)

Data_lmer <- Data_lmer[,fixed_revives:=revives/timeSurvived]
Data_lmer <- Data_lmer[,list(`before/after`,`positive/negative`,name,playerId,
                             createdAt,game_no,revives,fixed_revives,timeSurvived)]
Data_lmer <- Data_lmer[,revives_binary:=as.logical(ifelse(revives>0,1,0))]



# Testing LMM -------------------------------------------------------------

Model <- lmer(revives ~ (game_no| playerId) + offset(log(timeSurvived))  + 
              game_no+`positive/negative`+timeSurvived+heals+assists+damageDealt,
              data=Data_lmer[`before/after`=="before"])
summary(Model)

Model1 <- lmer(revives_binary ~ (game_no|| playerId) + 
                game_no*`before/after`*`positive/negative`,
              data=Data_lmer)
summary(Model1)
