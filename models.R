

####SETUP####
library(forecast)
library(tseries)
library(pracma)
library(rugarch)
####Loop through every address#####
##file to write to##
statistics <- file("PATH_TO_FILE/statistics.csv", 'a')
cat("ADDRESS,pdq,MSE_EMA,MSE_ARIMA,MSE_GARCH,MSE_GJRGARCH", file = statistics, sep="\n", append = TRUE)

addresses <- read.csv("PATH_TO_FILE/one_to_many.csv")
addresses <- addresses[-1,]

#Variables
i <- 1
MSE_LOG_EMA_FRAME <- list()
MSE_Log_ARIMA_FRAME <- list()
MSE_LOG_GARCH_FRAME <- list()
MSE_LOG_GJRGARCH_FRAME <- list()
ARIMA_ARMA_FRAME <- list()
for (address in addresses$ADDRESS) {
  address <- noquote(address)
  gsub(" ", "", address, fixed = TRUE)
  address_transactions_name <- paste("transaction_", address, ".csv", sep = '')
  print(address_transactions_name)
  
  data <- read.csv(address_transactions_name)
  
  ####EMA#####
  data$EMA <- movavg(data$VALUE, n = 20, type = 'e')
  EMAForecast <- forecast(data$EMA, h = 10)
  data$residuals <- data$VALUE - data$EMA
  MSE_EMA <- mean(data$residuals^2)
  sprintf("EMA MSE: %f",MSE_EMA)
  
  ###EMA log###
  data$EMA_LOG <- movavg(data$LOGVAL, n = 20, type = 'e')
  EMALogForecast <- forecast(data$EMA_LOG, h = 10)
  data$log_residuals <- data$LOGVAL - data$EMA_LOG
  MSE_LOG_EMA <- mean(data$log_residuals^2)
  sprintf("EMA MSE: %f",MSE_LOG_EMA)
  print(MSE_LOG_EMA)
  
  
  ####ARIMA####
  #Create Time Series Data
  valueTS = ts(data$VALUE, start = 0, end = max(data$ID))
  valueLogTS = ts(data$LOGVAL, start = 0, end = max(data$ID))
  plot(valueTS)
  #Check Autocorrelation, partial autocorrelation, and augmented Dickey-Fuller Test (pass <0.05)
  acf(valueTS)
  pacf(valueTS)
  adf.test(valueTS)
  
  #ARIMA Model Fitting 
  valueARIMA = auto.arima(valueTS, ic = "aic", trace = TRUE)
  valueARIMA$sigma2
  acf(ts(valueARIMA$residuals)) #
  pacf(ts(valueARIMA$residuals))
  
  #ARIMA Model Forecasting
  valueForecast = forecast(valueARIMA, level = c(95), 25)
  #Validate Data - Checking autocorrelation (< 0.05 = autocorrelation problems)
  Box.test(valueForecast$residuals, lag = 10,  type = "Ljung-Box")
  
  MSE_ARIMA <- mean(valueForecast$residuals^2)
  sprintf("ARIMA MSE: %f",MSE_ARIMA)
  
  ####ARIMA LOG######
  #Check Autocorrelation, partial autocorrelation, and augmented Dickey-Fuller Test (pass <0.05)
  acf(valueLogTS)
  pacf(valueLogTS)
  adf.test(valueLogTS)
  
  #ARIMA Model Fitting 
  valueLogARIMA = auto.arima(valueTS, ic = "aic", trace = TRUE)
  valueLogARIMA$sigma2
  acf(ts(valueLogARIMA$residuals)) #
  pacf(ts(valueLogARIMA$residuals))
  
  #ARIMA Model Forecasting
  valueLogForecast = forecast(valueLogARIMA, level = c(95), 25)
  #Validate Data - Checking autocorrelation (< 0.05 = autocorrelation problems)
  Box.test(valueLogForecast$residuals, lag = 10,  type = "Ljung-Box")
  
  MSE_LOG_ARIMA <- mean(valueLogForecast$residuals^2)
  sprintf("ARIMA MSE: %f",MSE_LOG_ARIMA)
  
  ####GARCH####
  #Model Specification
  ugspec = ugarchspec(variance.model = list(model = "sGARCH")) #Default ARMA(1,1)
  #ugspec = ugarchspec(mean.model =list(armaOrder = c (1,0)))
  
    #Model Estimation
  ugfit <- tryCatch({
    ugarchfit(spec = ugspec, data = data$LOGVAL)
    }, warning = function(war) {
    MSE_LOG_GARCH = NaN
    error1 <- -1
  }) 
  if (class(ugfit) == "uGARCHfit") {
    ugfit@fit$coef
    ug_var <- ugfit@fit$var
    ug_res2 <- ugfit@fit$residuals^2
    plot(ug_res2, type = "l")
    lines(ug_var, col = "green")
    
    #Model Forecasting
    ugfore <- ugarchforecast(ugfit, n.ahead = 10)
    ug_f <- ugfore@forecast$sigmaFor
    plot(ug_f, type = "l")
    
    MSE_LOG_GARCH <- mean(ug_res2)
    
  }
  else{
    MSE_LOG_GARCH <- NaN
  }
  
  ####GJR-GARCH####
  #Model Specification
  ugspec = ugarchspec(variance.model = list(model = "fGARCH", submodel = 'GJRGARCH')) #Default ARMA(1,1)
  #ugspec = ugarchspec(mean.model =list(armaOrder = c (1,0)))
  
  #Model Estimation
  ugfit <- tryCatch({
    ugarchfit(spec = ugspec, data = data$LOGVAL)
  }, warning = function(war) {
    MSE_LOG_GJRGARCH = NaN
    error2 = -1
  })
  if (class(ugfit) == "uGARCHfit") {
    ugfit@fit$coef
    ug_var <- ugfit@fit$var
    ug_res2 <- ugfit@fit$residuals^2
    plot(ug_res2, type = "l")
    lines(ug_var, col = "green")
    
    #Model Forecasting
    ugfore <- ugarchforecast(ugfit, n.ahead = 10)
    ug_f <- ugfore@forecast$sigmaFor
    plot(ug_f, type = "l")
    
    MSE_LOG_GJRGARCH <- mean(ug_res2)
  }
  else {
    MSE_LOG_GJRGARCH <- NaN
  }
  
  p <- valueLogARIMA$arma[1]
  d <- valueLogARIMA$arma[6]
  q <- valueLogARIMA$arma[2]
  pdq <- paste(p,d,q)
  
  entry <- paste(address,pdq,MSE_LOG_EMA,MSE_LOG_ARIMA,MSE_LOG_GJRGARCH,MSE_LOG_GARCH, sep = ",")
  cat(entry, file = statistics, sep = "\n", append = TRUE)
  
  MSE_LOG_EMA_FRAME <- append(MSE_LOG_EMA_FRAME, MSE_LOG_EMA)
  MSE_Log_ARIMA_FRAME <- append(MSE_Log_ARIMA_FRAME, MSE_LOG_ARIMA)
  MSE_LOG_GARCH_FRAME <- append(MSE_LOG_GARCH_FRAME, MSE_LOG_GARCH)
  MSE_LOG_GJRGARCH_FRAME <- append(MSE_LOG_GJRGARCH_FRAME, MSE_LOG_GJRGARCH)
  ARIMA_ARMA_FRAME <- append(ARIMA_ARMA_FRAME, pdq)
  i <- i+1
}

addresses$MSE_LOG_EMA <- MSE_LOG_EMA_FRAME
addresses$MSE_LOG_ARIMA <- MSE_Log_ARIMA_FRAME
addresses$MSE_LOG_GARCH <- MSE_LOG_GARCH_FRAME
addresses$MSE_LOG_GJRGARCH <- MSE_LOG_GJRGARCH_FRAME
addresses$pdq <- ARIMA_ARMA_FRAME

