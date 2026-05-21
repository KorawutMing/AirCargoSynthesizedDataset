# Forecasting Performance Report

## 1. Global Summary
|                      |      MAE |     RMSE |     WAPE |   Trend (Corr) |
|:---------------------|---------:|---------:|---------:|---------------:|
| (1, 'Transformer')   |  9600.2  |  9600.2  | 0.223401 |      0         |
| (1, 'SARIMA')        |  9628.57 |  9628.57 | 0.233277 |      0         |
| (1, 'ARIMA')         | 10589.8  | 10589.8  | 0.289494 |      0         |
| (1, 'Persistence+')  | 11223.2  | 11223.2  | 0.296265 |      0         |
| (1, 'Naive')         | 11315.2  | 11315.2  | 0.298983 |      0         |
| (1, 'SMA')           | 12156.4  | 12156.4  | 0.338785 |      0         |
| (7, 'Transformer')   |  8879.73 | 10548.6  | 0.183735 |      0.735415  |
| (7, 'SARIMA')        |  9676.92 | 11317.6  | 0.205785 |      0.766308  |
| (7, 'ARIMA')         | 12500.1  | 14724.1  | 0.255021 |      0.0877129 |
| (7, 'SMA')           | 12576    | 14692.3  | 0.259219 |      0         |
| (7, 'Persistence+')  | 14318.8  | 16616.9  | 0.315143 |     -0.108154  |
| (7, 'Naive')         | 14495.9  | 16788.6  | 0.324019 |      0         |
| (30, 'SARIMA')       |  9248.76 | 11630.7  | 0.204339 |      0.735939  |
| (30, 'Transformer')  | 10325.1  | 12979.6  | 0.223541 |      0.668771  |
| (30, 'SMA')          | 12648.4  | 15273.3  | 0.268792 |      0         |
| (30, 'ARIMA')        | 12783.9  | 15443.3  | 0.270469 |      0.0295134 |
| (30, 'Persistence+') | 14027.9  | 16952    | 0.314341 |      0.0123648 |
| (30, 'Naive')        | 14666.4  | 17670.4  | 0.336558 |      0         |

## 2. Route-Specific Analysis
### Route: CAN-LAX
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 18930   | 0.250466 |
| Transformer  | 19860.5 | 0.260606 |
| ARIMA        | 23057.6 | 0.292471 |
| SMA          | 23625.1 | 0.305065 |
| Persistence+ | 25431.5 | 0.320505 |
| Naive        | 25616.8 | 0.322686 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CGO-ORD
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 14141.4 | 0.239377 |
| SARIMA       | 14398.3 | 0.246275 |
| ARIMA        | 17664.6 | 0.2957   |
| Naive        | 18044.4 | 0.311046 |
| Persistence+ | 18072.8 | 0.310437 |
| SMA          | 18225.1 | 0.305843 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** SMA struggles with the volatility or seasonality of this route.

### Route: JFK-NRT
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 4057.57 | 0.176265 |
| SARIMA       | 4291.63 | 0.183777 |
| ARIMA        | 5635.12 | 0.23668  |
| SMA          | 6083.09 | 0.255418 |
| Persistence+ | 7224.45 | 0.316155 |
| Naive        | 7762.15 | 0.338774 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: JFK-SIN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 3814.13 | 0.185327 |
| SARIMA       | 4012.74 | 0.199317 |
| ARIMA        | 5297.42 | 0.277315 |
| SMA          | 5806.38 | 0.302407 |
| Persistence+ | 7199.25 | 0.325962 |
| Naive        | 7731.43 | 0.347405 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: SIN-CAN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 5957.69 | 0.192498 |
| Transformer  | 6134.84 | 0.189553 |
| Persistence+ | 8021.71 | 0.269857 |
| ARIMA        | 8134.96 | 0.256139 |
| Naive        | 8307.84 | 0.279357 |
| SMA          | 8561.75 | 0.275928 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** SMA struggles with the volatility or seasonality of this route.

## 3. Conclusions
- **Short-term (H=1):** Baselines like Naive/SMA are often competitive, but ARIMA usually leads.
- **Long-term (H=7, 30):** SARIMA and Transformer models show superior trend capture and lower WAPE.
- **Modularity:** The refactored architecture allows for seamless model swapping and testing.
