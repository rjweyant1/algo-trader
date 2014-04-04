
require(lattice)
# calculates the average of 1) the maximum of the signed distances of xi from its k left neighbors
# and the max of the signed distance to the right k neigbhors.
# Indicates 'signficance' of peak
S1<-function(k,i,x){
  return((max(x[i]-x[(i-k):(i-1)])+max(x[i]-x[(i+1):(i+k)]))/2)
}
S1<-function(k,i,x){
  return(x[i]-(max(x[(i-k):(i-1)])+max(x[(i+1):(i+k)]))/2  )
}
beta<-function(x,i,j){
  val = x[i:j]
  time = 0:(j-i)
  dat = data.frame(val=val,time=time)
  mod = lm(val~time,data=dat)  
  summary = summary(mod)
  slope = mod$coefficients[2]
  se = sqrt(summary$cov.unscaled[2,2])
  return(slope)
}


#
moving.derivative<-function(x,k){
  d=c()
  for (i in 1:length(x)){
    if(i <= k & i > 1 & !is.na(x[i])){
      #d[i] = beta2(x,1,i)
      d[i] = beta(x,1,i)
    }
    else  if (i>30 & i >1 & !is.na(x[i])){
      #d[i] = beta2(x,i-k,i)
      d[i] = beta(x,i-k,i)
    }
  }
  if(is.na(d[1]) & !is.na(d[2])){
    d[1]=d[2]
  }
  return(d)
}
#
moving.average<-function(x,k){
  ma=c()
  for (i in 1:length(x)){
    if(i <= k){
      ma[i] = mean(x[1:i])
    }
    else{
      ma[i] = ma[i-1]+ (x[i] - x[i-k])/k
    }
  }
  return(ma)
}
trade.btc.to.usd<-function(btc,rate){
  return(btc*rate)
}
trade.usd.to.btc<-function(usd,rate){
  return(usd/rate)
}

##############

k=30
h=1
N=500

basicPeak = 10*sin((1:(N)*pi)/N)
noiseyPeak = sin((1:(5*N))*pi/N)+rnorm(N,0,0.09)
x = noiseyPeak + abs(min(noiseyPeak)) + 1
plot(x)

k=30
k.ma=150
n = length(x)

curData = data.frame(rate=x,time=1:n)
head(curData)

plot(rate~time,type='l',data=curData)

d1.30 = data.frame(d1 = moving.derivative(curData$rate,k), time = 1:n)
d1.30.ma = data.frame(d1 = moving.average(d1.30$d1,100), time = 1:n)
d2.30 = data.frame(d2 = moving.derivative(d1.30.ma$d1,30), time = 1:n)
d2.30.ma = data.frame(d2 =  moving.average(d2.30$d2,100), time = 1:n)


money = data.frame(time=1:n,btc=0,usd=100)
head(money)

timer = 0
for(i in 600:3000){
  
  if(d1.30.ma$d1[i-1] < 0 && d1.30.ma$d1[i] > 0 && timer == 0){
    newBTC = trade.usd.to.btc(usd=money$usd[i],rate=curData$rate[i])
    print('border crossing')
    print(paste(i,': Trade ', money$usd[money$time == i], ' for ',curData$rate[i], ' to get ', newBTC,sep=''))
    
    money$usd[money$time >= i] = 0
    
    money$btc[money$time >=i] = money$btc[money$time >=i] + newBTC
    
    timer = 30
  }
  if(d1.30.ma$d1[i-1] > 0 && d1.30.ma$d1[i] < 0 && timer == 0){
    newUSD = trade.btc.to.usd(btc=money$btc[i],rate=curData$rate[i])
    print('border crossing')
    print(paste(i,': Trade ', money$btc[money$time == i], ' for ',curData$rate[i], ' to get ', newUSD,sep=''))
    money$btc[money$time >=i] = 0
    
    money$usd[money$time >= i] = money$usd[money$time >= i] + newUSD
    
    timer = 30
  }  
  
  if(timer > 0){
    timer = timer -1
  }
  
  
}
newUSD


#money
plot(btc~time,type='l',lwd=4,col=2,data=money)
par(new=T)
plot(usd~time,type='l',lwd=5,col=3,data=money)
par(new=T)
plot(rate~time,type='l',data=curData,xlim=c(0,n))
par(new=T)
plot(d1~time,type='l',col=7,lwd=2,d1.30.ma[30:n,],xlim=c(0,3000))
par(new=T)
plot(d2~time,type='l',col=6,lwd=2,d2.30.ma[300:n,],xlim=c(0,3000))

head(d1.30.ma)
head(d2.30.ma)


## plots
plot(rate~time,type='l',data=curData,xlim=c(0,3000))
#par(new=T)
#plot(d1~time,type='l',col=2,lwd=3,d1.30[30:n,],xlim=c(0,3000))
#par(new=T)
#plot(d2~time,type='l',col=4,lwd=3,d2.30[100:n,],xlim=c(0,3000))

par(new=T)
plot(d1~time,type='l',col=3,lwd=3,d1.30.ma[30:n,],xlim=c(0,3000))
par(new=T)
plot(d2~time,type='l',col=6,lwd=3,d2.30.ma[300:n,],xlim=c(0,3000))



x.ma<-moving.average(x,k)
beta.ma.30<-moving.average(a,30)
beta.ma.100<-moving.average(a,100)
beta.ma.1000<-moving.average(a,1000)





plot(x.ma,type='l',col=2)
par(new=T)
plot(a,type='l',col=3)
par(new=T)
plot(beta.ma.30,type='l',col=4)
par(new=T)
plot(beta.ma.100,type='l',col=4)
par(new=T)
plot(beta.ma.1000,type='l',col=4)

par(new=F)


n = length(x)-k
a=c()
for(i in (k+1):(n-k)){
  a[i-k] = beta2(k,i,x)
}

plot(a,type='p')



#





m.prime=mean(a)
s.prime=sd(a)
for(i in 1:n){
  print(i)
  print(paste('a[i]:',a[i],'\tm.prime:',m.prime,'\ts.prime:',s.prime))
  print(paste('a[i]-m.prime:',a[i]-m.prime))
  print(paste('h*s.prime',h*s.prime))
  if(a[i]>0 && (a[i]-m.prime) > (h*s.prime)){
    print('Peak')
    O=append(O,x)
  }  
}






ma=c()
alpha=0.9
for(i in 1:length(x)){
  if(i == 1){
    ma[i]<-x[i]
  }
  else{
    print(x[i])
    ma[i] = (1-alpha)*ma[i-1] + x[i]
  }
}
ma
plot(ma)

plot((x - ma)/ma)



beta2<-function(k,i,x){
  val = x[(i-k):i]
  time = 0:k
  dat = data.frame(val=val,time=time)
  mod = lm(val~time,data=dat)  
  summary = summary(mod)
  slope = mod$coefficients[2]
  se = sqrt(summary$cov.unscaled[2,2])
  return(slope)
}
