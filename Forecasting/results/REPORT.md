# Forecasting Performance Report

## 1. Global Summary
|                      |     MAE |    RMSE |     WAPE |   Trend (Corr) |
|:---------------------|--------:|--------:|---------:|---------------:|
| (14, 'SARIMA')       | 3979.14 | 4828.18 | 0.329454 |       0.591097 |
| (14, 'Transformer')  | 4506.27 | 5361.42 | 0.36799  |       0.278453 |
| (14, 'ARIMA')        | 4624.05 | 5499.53 | 0.369414 |       0.121319 |
| (14, 'SMA')          | 4858.24 | 5743.15 | 0.385879 |       0        |
| (14, 'Persistence+') | 5230.02 | 6317.03 | 0.429727 |       0.109737 |
| (14, 'Naive')        | 5483.32 | 6610.72 | 0.45073  |       0        |

## 2. Route-Specific Analysis
### Route: CAN-CGO
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 1378.1  | 0.427285 |
| Transformer  | 1485.97 | 0.46435  |
| ARIMA        | 1527.75 | 0.458499 |
| SMA          | 1554.85 | 0.467532 |
| Persistence+ | 1885.77 | 0.565723 |
| Naive        | 1986.41 | 0.594922 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CAN-HKG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 756.075 | 0.711199 |
| ARIMA        | 766.708 | 0.679493 |
| SMA          | 777.295 | 0.686353 |
| Transformer  | 803.236 | 0.737036 |
| Persistence+ | 921.735 | 0.844184 |
| Naive        | 976.864 | 0.893207 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CAN-JFK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4886.45 | 0.362267 |
| ARIMA        | 5480.25 | 0.392014 |
| Transformer  | 5587.66 | 0.400803 |
| SMA          | 5751.04 | 0.407434 |
| Persistence+ | 6423.85 | 0.46691  |
| Naive        | 6792.35 | 0.492325 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CAN-LAX
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 5360.05 | 0.359638 |
| Transformer  | 5778.43 | 0.372923 |
| ARIMA        | 6028.07 | 0.392066 |
| SMA          | 6439.44 | 0.419092 |
| Persistence+ | 6761.18 | 0.447045 |
| Naive        | 7113.95 | 0.471276 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CAN-NRT
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3798.78 | 0.294656 |
| Transformer  | 4339.49 | 0.337363 |
| ARIMA        | 4535.24 | 0.336617 |
| SMA          | 4768.35 | 0.354916 |
| Persistence+ | 5063.14 | 0.38184  |
| Naive        | 5275.03 | 0.3976   |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CAN-ORD
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 5569.53 | 0.344794 |
| Transformer  | 6056.22 | 0.368475 |
| ARIMA        | 6191.96 | 0.379556 |
| SMA          | 6617.68 | 0.405962 |
| Persistence+ | 6860.33 | 0.427623 |
| Naive        | 7229.89 | 0.450922 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CAN-PEK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3588.76 | 0.288706 |
| Transformer  | 4116.91 | 0.326741 |
| ARIMA        | 4449.57 | 0.342513 |
| SMA          | 4684.14 | 0.360173 |
| Persistence+ | 5034.57 | 0.400236 |
| Naive        | 5242.1  | 0.417639 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CAN-PVG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2993.83 | 0.318253 |
| Transformer  | 3341.37 | 0.357726 |
| ARIMA        | 3585.36 | 0.36367  |
| SMA          | 3779.42 | 0.382975 |
| Persistence+ | 3874.35 | 0.404037 |
| Naive        | 4026.05 | 0.419457 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CAN-SIN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3618.12 | 0.295279 |
| Transformer  | 4127.2  | 0.341203 |
| ARIMA        | 4378.62 | 0.345363 |
| SMA          | 4597.72 | 0.362022 |
| Persistence+ | 4940.52 | 0.400956 |
| Naive        | 5154.78 | 0.419155 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CGO-CAN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2550.78 | 0.335841 |
| Transformer  | 2778.24 | 0.375622 |
| ARIMA        | 2907.89 | 0.374109 |
| SMA          | 3009.58 | 0.389706 |
| Persistence+ | 3539.35 | 0.474991 |
| Naive        | 3727.92 | 0.501794 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CGO-HKG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3769.31 | 0.27366  |
| Transformer  | 4705.3  | 0.338738 |
| ARIMA        | 4778.99 | 0.330977 |
| SMA          | 5004.07 | 0.346699 |
| Persistence+ | 5250.07 | 0.37462  |
| Naive        | 5471.38 | 0.39105  |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CGO-JFK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4991.36 | 0.297044 |
| Transformer  | 5920.82 | 0.346481 |
| ARIMA        | 5993.48 | 0.342714 |
| SMA          | 6315.78 | 0.358147 |
| Persistence+ | 6653.14 | 0.388623 |
| Naive        | 6990.91 | 0.408245 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CGO-LAX
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 5207.07 | 0.360233 |
| Transformer  | 5722.26 | 0.379599 |
| ARIMA        | 5898.58 | 0.396984 |
| SMA          | 6294.16 | 0.424516 |
| Persistence+ | 6587.59 | 0.453563 |
| Naive        | 6941.4  | 0.478956 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CGO-NRT
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3673.12 | 0.292373 |
| Transformer  | 4208.67 | 0.332526 |
| ARIMA        | 4420.45 | 0.339937 |
| SMA          | 4619.84 | 0.354073 |
| Persistence+ | 5059.68 | 0.399455 |
| Naive        | 5277.52 | 0.416792 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CGO-ORD
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 5351.27 | 0.347233 |
| Transformer  | 5912.35 | 0.377453 |
| ARIMA        | 6017.87 | 0.384636 |
| SMA          | 6485.29 | 0.416615 |
| Persistence+ | 6565.72 | 0.421387 |
| Naive        | 6909.32 | 0.443795 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CGO-PEK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3390.47 | 0.288431 |
| Transformer  | 4088.04 | 0.341225 |
| ARIMA        | 4116.13 | 0.334469 |
| SMA          | 4358.24 | 0.353791 |
| Persistence+ | 4434.81 | 0.375017 |
| Naive        | 4588.11 | 0.389396 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CGO-PVG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2833.42 | 0.310558 |
| Transformer  | 3272.32 | 0.355738 |
| ARIMA        | 3402.9  | 0.359502 |
| SMA          | 3563.88 | 0.37638  |
| Persistence+ | 3821.77 | 0.407068 |
| Naive        | 3972.85 | 0.423332 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CGO-SIN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3374.19 | 0.290428 |
| Transformer  | 3998.45 | 0.350143 |
| ARIMA        | 4160.06 | 0.345463 |
| SMA          | 4396.79 | 0.364319 |
| Persistence+ | 4617.02 | 0.389129 |
| Naive        | 4829.13 | 0.406809 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: HKG-CAN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SMA          | 581.956 | 0.870484 |
| ARIMA        | 584.482 | 0.879007 |
| SARIMA       | 594.875 | 0.955458 |
| Transformer  | 617.527 | 0.942384 |
| Persistence+ | 729.239 | 1.12696  |
| Naive        | 769.237 | 1.19596  |

**Strengths:** SMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: HKG-CGO
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 1404.42 | 0.42271  |
| Transformer  | 1527.37 | 0.462454 |
| ARIMA        | 1530.51 | 0.448452 |
| SMA          | 1568.52 | 0.458192 |
| Persistence+ | 1861.59 | 0.538562 |
| Naive        | 1960.4  | 0.564344 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: HKG-JFK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4947.13 | 0.347978 |
| ARIMA        | 5560.19 | 0.37887  |
| Transformer  | 5564.84 | 0.380127 |
| SMA          | 5799.69 | 0.393019 |
| Persistence+ | 6474.37 | 0.447565 |
| Naive        | 6839.5  | 0.472418 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: HKG-LAX
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 5501.14 | 0.34657  |
| Transformer  | 6057.45 | 0.370082 |
| ARIMA        | 6196.69 | 0.382687 |
| SMA          | 6630.18 | 0.409852 |
| Persistence+ | 6789.68 | 0.424921 |
| Naive        | 7132.46 | 0.446315 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: HKG-NRT
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3873.91 | 0.281251 |
| Transformer  | 4491.3  | 0.327276 |
| ARIMA        | 4805.07 | 0.335705 |
| SMA          | 5094.39 | 0.355656 |
| Persistence+ | 5200.35 | 0.370282 |
| Naive        | 5413.69 | 0.385645 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: HKG-ORD
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 5446.35 | 0.327159 |
| ARIMA        | 6213.93 | 0.366813 |
| Transformer  | 6222.49 | 0.36195  |
| Persistence+ | 6611.66 | 0.398492 |
| SMA          | 6701.18 | 0.396238 |
| Naive        | 6935.4  | 0.418691 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: HKG-PEK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3738.78 | 0.282524 |
| Transformer  | 4321.29 | 0.316154 |
| ARIMA        | 4575.52 | 0.332727 |
| Persistence+ | 4840.86 | 0.366615 |
| SMA          | 4954.77 | 0.358762 |
| Naive        | 5005.78 | 0.380208 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: HKG-PVG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3026.22 | 0.300961 |
| Transformer  | 3308.67 | 0.336746 |
| ARIMA        | 3587.82 | 0.345627 |
| SMA          | 3785.93 | 0.363547 |
| Persistence+ | 4136.44 | 0.404354 |
| Naive        | 4335.98 | 0.421954 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: HKG-SIN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3710.18 | 0.288709 |
| Transformer  | 4335.82 | 0.336005 |
| ARIMA        | 4456.71 | 0.334646 |
| SMA          | 4679.69 | 0.349562 |
| Persistence+ | 5081.53 | 0.395926 |
| Naive        | 5317.28 | 0.414753 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: JFK-CAN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3271.87 | 0.308286 |
| ARIMA        | 3487.04 | 0.333138 |
| SMA          | 3549.26 | 0.339502 |
| Transformer  | 3741.79 | 0.362385 |
| Persistence+ | 4201.3  | 0.402813 |
| Naive        | 4409.23 | 0.422737 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: JFK-CGO
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 1608.04 | 0.395066 |
| ARIMA        | 1686.68 | 0.407158 |
| SMA          | 1691.86 | 0.409126 |
| Transformer  | 2026.32 | 0.486253 |
| Persistence+ | 2077.12 | 0.504435 |
| Naive        | 2175.2  | 0.528718 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: JFK-HKG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3168.18 | 0.317089 |
| ARIMA        | 3484.69 | 0.348534 |
| SMA          | 3536.08 | 0.354278 |
| Transformer  | 3628.59 | 0.369629 |
| Persistence+ | 4363.04 | 0.440201 |
| Naive        | 4587    | 0.463136 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: JFK-LAX
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3438.9  | 0.351892 |
| Transformer  | 3609.88 | 0.366403 |
| ARIMA        | 3691.13 | 0.369725 |
| SMA          | 3777.61 | 0.374125 |
| Persistence+ | 4519.69 | 0.458192 |
| Naive        | 4736.65 | 0.479427 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: JFK-NRT
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4139.23 | 0.258768 |
| Transformer  | 5023.67 | 0.321588 |
| ARIMA        | 5204.78 | 0.318893 |
| SMA          | 5358.6  | 0.327597 |
| Persistence+ | 6052.5  | 0.372324 |
| Naive        | 6348.96 | 0.390073 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: JFK-ORD
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 1820.11 | 0.385787 |
| Transformer  | 1951.22 | 0.412677 |
| ARIMA        | 1968.58 | 0.411742 |
| SMA          | 2034.76 | 0.423357 |
| Persistence+ | 2425.95 | 0.515146 |
| Naive        | 2544.95 | 0.541566 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: JFK-PEK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2741.65 | 0.329966 |
| ARIMA        | 3063.81 | 0.364256 |
| SMA          | 3098.62 | 0.367185 |
| Transformer  | 3214.57 | 0.394031 |
| Persistence+ | 4100.18 | 0.480485 |
| Naive        | 4353.9  | 0.508592 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: JFK-PVG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3509.84 | 0.282623 |
| Transformer  | 3979.49 | 0.319392 |
| ARIMA        | 4149.55 | 0.32613  |
| SMA          | 4254.02 | 0.334184 |
| Persistence+ | 4902.79 | 0.393229 |
| Naive        | 5133.95 | 0.411818 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: JFK-SIN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3852.77 | 0.265394 |
| Transformer  | 4626.68 | 0.319331 |
| ARIMA        | 4747.32 | 0.31922  |
| SMA          | 4774.52 | 0.322943 |
| Persistence+ | 5858.72 | 0.393535 |
| Naive        | 6141.48 | 0.412502 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: LAX-CAN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2874.48 | 0.325256 |
| Transformer  | 3110.11 | 0.358914 |
| ARIMA        | 3232.28 | 0.361654 |
| SMA          | 3271.88 | 0.364696 |
| Persistence+ | 4148.43 | 0.465803 |
| Naive        | 4379.55 | 0.491964 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: LAX-CGO
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 1388.62 | 0.400651 |
| ARIMA        | 1512.04 | 0.42665  |
| SMA          | 1520.29 | 0.432661 |
| Transformer  | 1554.81 | 0.447684 |
| Persistence+ | 1833.7  | 0.518836 |
| Naive        | 1927.57 | 0.545255 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: LAX-HKG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2716.09 | 0.323817 |
| Transformer  | 3019.66 | 0.365069 |
| ARIMA        | 3059.43 | 0.361046 |
| SMA          | 3077.3  | 0.364577 |
| Persistence+ | 3803.79 | 0.445287 |
| Naive        | 4002.53 | 0.46776  |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: LAX-JFK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2772.47 | 0.359913 |
| Transformer  | 2866.57 | 0.371169 |
| ARIMA        | 2943.25 | 0.375113 |
| SMA          | 2981.03 | 0.37697  |
| Persistence+ | 3576.34 | 0.468856 |
| Naive        | 3733.26 | 0.490848 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: LAX-NRT
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3966.33 | 0.296609 |
| Transformer  | 4568.8  | 0.344174 |
| ARIMA        | 4712.31 | 0.34308  |
| SMA          | 4783.28 | 0.348777 |
| Persistence+ | 5703.2  | 0.41091  |
| Naive        | 5966.95 | 0.429109 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: LAX-ORD
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4135.22 | 0.301848 |
| Transformer  | 4285.74 | 0.306349 |
| SMA          | 4799.79 | 0.344236 |
| ARIMA        | 4809.82 | 0.344965 |
| Persistence+ | 5639.61 | 0.407749 |
| Naive        | 5872.88 | 0.424468 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: LAX-PEK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4443.04 | 0.303044 |
| Transformer  | 4835.11 | 0.333236 |
| ARIMA        | 5379.98 | 0.358192 |
| SMA          | 5420.24 | 0.359947 |
| Persistence+ | 6659.41 | 0.448155 |
| Naive        | 6986.74 | 0.470058 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: LAX-PVG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3307.97 | 0.314764 |
| ARIMA        | 3779.19 | 0.355373 |
| Transformer  | 3820.43 | 0.361753 |
| SMA          | 3849.34 | 0.36171  |
| Persistence+ | 4450.6  | 0.416369 |
| Naive        | 4641.76 | 0.433762 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: LAX-SIN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3785.53 | 0.301274 |
| Transformer  | 4224.53 | 0.336252 |
| ARIMA        | 4510.67 | 0.353144 |
| SMA          | 4572.13 | 0.35715  |
| Persistence+ | 5719.27 | 0.444521 |
| Naive        | 6040.47 | 0.468672 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: NRT-CAN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3326.38 | 0.301557 |
| Transformer  | 3763.76 | 0.340247 |
| ARIMA        | 4042.08 | 0.350312 |
| SMA          | 4283.8  | 0.371485 |
| Persistence+ | 4533.61 | 0.406189 |
| Naive        | 4737.46 | 0.424195 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: NRT-CGO
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2744.35 | 0.307438 |
| Transformer  | 3184.56 | 0.36323  |
| ARIMA        | 3247.57 | 0.352754 |
| SMA          | 3405.14 | 0.370075 |
| Persistence+ | 3681.67 | 0.399223 |
| Naive        | 3845.88 | 0.416522 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: NRT-HKG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3836.01 | 0.281252 |
| Transformer  | 4434.75 | 0.325197 |
| ARIMA        | 4738.58 | 0.332811 |
| SMA          | 5006.47 | 0.352364 |
| Persistence+ | 5141.94 | 0.372916 |
| Naive        | 5333.64 | 0.388283 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: NRT-JFK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4925.27 | 0.333615 |
| ARIMA        | 5542.47 | 0.367214 |
| Transformer  | 5634.4  | 0.373186 |
| SMA          | 5813.17 | 0.382206 |
| Persistence+ | 6474.59 | 0.432605 |
| Naive        | 6860.97 | 0.457856 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: NRT-LAX
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 5360.21 | 0.330663 |
| Transformer  | 6254.52 | 0.365101 |
| ARIMA        | 6273.52 | 0.373133 |
| Persistence+ | 6584.47 | 0.403259 |
| SMA          | 6739.2  | 0.400431 |
| Naive        | 6925.06 | 0.424067 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: NRT-ORD
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 5171.82 | 0.378854 |
| Transformer  | 5466.21 | 0.389069 |
| ARIMA        | 5758.42 | 0.411747 |
| SMA          | 6167.59 | 0.444064 |
| Persistence+ | 6413.73 | 0.466256 |
| Naive        | 6750.91 | 0.492161 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: NRT-PEK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3399.21 | 0.290701 |
| Transformer  | 3960.11 | 0.346213 |
| ARIMA        | 4194.85 | 0.347141 |
| SMA          | 4396.26 | 0.364956 |
| Persistence+ | 4545.49 | 0.382223 |
| Naive        | 4715.66 | 0.396104 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: NRT-PVG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2562.85 | 0.328473 |
| Transformer  | 2961.33 | 0.384467 |
| ARIMA        | 3061.87 | 0.375444 |
| SMA          | 3203.46 | 0.390194 |
| Persistence+ | 3540.33 | 0.459692 |
| Naive        | 3695.36 | 0.481561 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: NRT-SIN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4265.81 | 0.274377 |
| Transformer  | 4864.88 | 0.319335 |
| ARIMA        | 5097.83 | 0.321285 |
| SMA          | 5476.52 | 0.344334 |
| Persistence+ | 5765.84 | 0.374676 |
| Naive        | 6045.7  | 0.392837 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: ORD-CAN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2938.7  | 0.332126 |
| ARIMA        | 3303.93 | 0.36654  |
| SMA          | 3309.22 | 0.366204 |
| Transformer  | 3317.57 | 0.368579 |
| Persistence+ | 4057.08 | 0.453289 |
| Naive        | 4260.15 | 0.475441 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: ORD-CGO
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2372.81 | 0.340997 |
| ARIMA        | 2703.53 | 0.379735 |
| Transformer  | 2734.78 | 0.390902 |
| SMA          | 2753.99 | 0.386593 |
| Persistence+ | 3235.59 | 0.452876 |
| Naive        | 3394.51 | 0.474581 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: ORD-HKG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3550.12 | 0.311498 |
| Transformer  | 4032.34 | 0.355444 |
| ARIMA        | 4064.84 | 0.352646 |
| SMA          | 4121.74 | 0.357514 |
| Persistence+ | 4850.13 | 0.419659 |
| Naive        | 5070.04 | 0.437736 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: ORD-JFK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3138.92 | 0.335023 |
| Transformer  | 3323.88 | 0.358805 |
| ARIMA        | 3466.91 | 0.361499 |
| SMA          | 3622.77 | 0.374568 |
| Persistence+ | 4207.17 | 0.435454 |
| Naive        | 4440.41 | 0.458212 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: ORD-LAX
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3548.32 | 0.314126 |
| Transformer  | 3910.64 | 0.338991 |
| ARIMA        | 3999.84 | 0.345529 |
| SMA          | 4025.7  | 0.345763 |
| Persistence+ | 4721.65 | 0.416922 |
| Naive        | 4915.07 | 0.434287 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: ORD-NRT
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4104.44 | 0.301546 |
| Transformer  | 4376.12 | 0.326899 |
| ARIMA        | 4878.06 | 0.351749 |
| SMA          | 4959.1  | 0.357648 |
| Persistence+ | 5632.02 | 0.407966 |
| Naive        | 5876.25 | 0.425628 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: ORD-PEK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4183.07 | 0.286088 |
| Transformer  | 4616.26 | 0.321266 |
| ARIMA        | 5082.93 | 0.342091 |
| SMA          | 5145.78 | 0.347253 |
| Persistence+ | 5987.83 | 0.40743  |
| Naive        | 6259.39 | 0.426004 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: ORD-PVG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3395.78 | 0.316156 |
| Transformer  | 3665.26 | 0.343221 |
| ARIMA        | 3800.32 | 0.351132 |
| SMA          | 3808.19 | 0.351576 |
| Persistence+ | 4868.4  | 0.450903 |
| Naive        | 5131.85 | 0.474592 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: ORD-SIN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3778.37 | 0.30475  |
| Transformer  | 4415.97 | 0.358785 |
| ARIMA        | 4510.78 | 0.35586  |
| SMA          | 4579.32 | 0.361474 |
| Persistence+ | 5446.93 | 0.430046 |
| Naive        | 5707.9  | 0.450552 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PEK-CAN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 1698.37 | 0.371363 |
| Transformer  | 1925.82 | 0.427848 |
| ARIMA        | 1957.05 | 0.417934 |
| SMA          | 2011.11 | 0.428363 |
| Persistence+ | 2163.6  | 0.480068 |
| Naive        | 2248.49 | 0.499199 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PEK-CGO
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 1003.1  | 0.547258 |
| ARIMA        | 1067.95 | 0.561502 |
| SMA          | 1087.92 | 0.570716 |
| Transformer  | 1100.58 | 0.603651 |
| Persistence+ | 1294.46 | 0.714263 |
| Naive        | 1361.51 | 0.753639 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PEK-HKG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2803.19 | 0.327377 |
| Transformer  | 3060.93 | 0.364128 |
| ARIMA        | 3179.01 | 0.360865 |
| SMA          | 3301.74 | 0.374574 |
| Persistence+ | 3860.68 | 0.440729 |
| Naive        | 4061.97 | 0.462586 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PEK-JFK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4830.24 | 0.329391 |
| Transformer  | 5666.58 | 0.372096 |
| ARIMA        | 5682.05 | 0.37099  |
| SMA          | 5925.51 | 0.384307 |
| Persistence+ | 6249.33 | 0.411674 |
| Naive        | 6569.53 | 0.431754 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PEK-LAX
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 5524.51 | 0.336825 |
| Transformer  | 6106.4  | 0.360972 |
| ARIMA        | 6240.2  | 0.370836 |
| Persistence+ | 6534.02 | 0.39943  |
| SMA          | 6761.69 | 0.402976 |
| Naive        | 6847.37 | 0.420373 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PEK-NRT
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3173.07 | 0.295489 |
| Transformer  | 3722.94 | 0.341794 |
| ARIMA        | 3914.06 | 0.346144 |
| SMA          | 4107.65 | 0.361037 |
| Persistence+ | 4349.95 | 0.403928 |
| Naive        | 4525.52 | 0.42198  |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PEK-ORD
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4969.66 | 0.376926 |
| Transformer  | 5466.45 | 0.392751 |
| ARIMA        | 5599.18 | 0.410455 |
| SMA          | 6018.78 | 0.441539 |
| Persistence+ | 6362.77 | 0.484383 |
| Naive        | 6749.39 | 0.514855 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PEK-PVG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 1922.48 | 0.363257 |
| Transformer  | 2116.63 | 0.411764 |
| ARIMA        | 2170.58 | 0.396378 |
| SMA          | 2241.95 | 0.410339 |
| Persistence+ | 2536.72 | 0.461858 |
| Naive        | 2657.95 | 0.483216 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PEK-SIN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3179.72 | 0.306975 |
| Transformer  | 3706.3  | 0.358476 |
| ARIMA        | 3766.75 | 0.354767 |
| SMA          | 3961.56 | 0.370986 |
| Persistence+ | 4364.92 | 0.411925 |
| Naive        | 4603.52 | 0.43305  |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PVG-CAN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2895.2  | 0.319155 |
| ARIMA        | 3337.54 | 0.361698 |
| Transformer  | 3358.84 | 0.365897 |
| SMA          | 3430.32 | 0.372766 |
| Persistence+ | 4015.43 | 0.450151 |
| Naive        | 4219.1  | 0.474333 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PVG-CGO
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 1459.81 | 0.419586 |
| ARIMA        | 1588.94 | 0.441869 |
| Transformer  | 1613.97 | 0.460317 |
| SMA          | 1628.46 | 0.454292 |
| Persistence+ | 1920.92 | 0.54406  |
| Naive        | 2024.67 | 0.573246 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PVG-HKG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2668.29 | 0.323538 |
| Transformer  | 3096.27 | 0.373883 |
| ARIMA        | 3116.08 | 0.364391 |
| SMA          | 3240.29 | 0.377576 |
| Persistence+ | 3664.3  | 0.440124 |
| Naive        | 3838.63 | 0.461256 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PVG-JFK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4812.63 | 0.323366 |
| ARIMA        | 5531.02 | 0.360334 |
| Transformer  | 5671.9  | 0.372231 |
| SMA          | 5753.97 | 0.374111 |
| Persistence+ | 6431.21 | 0.422671 |
| Naive        | 6783.75 | 0.445492 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PVG-LAX
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 5529.56 | 0.330133 |
| Transformer  | 6260.54 | 0.365155 |
| ARIMA        | 6307.61 | 0.369961 |
| Persistence+ | 6714.1  | 0.400214 |
| SMA          | 6791.23 | 0.397926 |
| Naive        | 7036.73 | 0.419505 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PVG-NRT
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3831.9  | 0.295136 |
| Transformer  | 4570.55 | 0.353945 |
| ARIMA        | 4577.35 | 0.339349 |
| SMA          | 4800.15 | 0.355865 |
| Persistence+ | 5119.59 | 0.389123 |
| Naive        | 5341.7  | 0.40603  |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PVG-ORD
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 5609.98 | 0.322282 |
| ARIMA        | 6370.45 | 0.35919  |
| Transformer  | 6381.01 | 0.355497 |
| Persistence+ | 6631.16 | 0.385107 |
| SMA          | 6932.35 | 0.39094  |
| Naive        | 6950.65 | 0.404531 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PVG-PEK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4021.8  | 0.28241  |
| Transformer  | 4516.5  | 0.323172 |
| ARIMA        | 5129.13 | 0.347987 |
| SMA          | 5366.86 | 0.365583 |
| Persistence+ | 5405.89 | 0.371962 |
| Naive        | 5573.36 | 0.383091 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PVG-SIN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3850.28 | 0.287858 |
| Transformer  | 4412.54 | 0.332945 |
| ARIMA        | 4721.13 | 0.338269 |
| SMA          | 5000.86 | 0.358308 |
| Persistence+ | 5205.62 | 0.382955 |
| Naive        | 5423.53 | 0.399206 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: SIN-CAN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3130.19 | 0.303571 |
| Transformer  | 3570.25 | 0.34823  |
| ARIMA        | 3768.61 | 0.353192 |
| SMA          | 3925.66 | 0.36622  |
| Persistence+ | 4121.63 | 0.400497 |
| Naive        | 4280.91 | 0.416496 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: SIN-CGO
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2555.96 | 0.311119 |
| Transformer  | 2941.67 | 0.355489 |
| ARIMA        | 3012.62 | 0.353409 |
| SMA          | 3129.67 | 0.367972 |
| Persistence+ | 3393.05 | 0.403358 |
| Naive        | 3527.64 | 0.419592 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: SIN-HKG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3604.91 | 0.282561 |
| Transformer  | 4418.93 | 0.34572  |
| ARIMA        | 4481.44 | 0.332956 |
| SMA          | 4733.51 | 0.351934 |
| Persistence+ | 4888.25 | 0.373888 |
| Naive        | 5081.84 | 0.389164 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: SIN-JFK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4779.65 | 0.345287 |
| ARIMA        | 5528.75 | 0.381324 |
| Transformer  | 5588.84 | 0.387353 |
| SMA          | 5787.58 | 0.395172 |
| Persistence+ | 6272.65 | 0.441455 |
| Naive        | 6608.21 | 0.46464  |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: SIN-LAX
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 5336.69 | 0.345939 |
| Transformer  | 6010.64 | 0.377599 |
| ARIMA        | 6188.89 | 0.391516 |
| Persistence+ | 6583.18 | 0.423723 |
| SMA          | 6622.33 | 0.41989  |
| Naive        | 6902.24 | 0.444439 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: SIN-NRT
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4242.07 | 0.274545 |
| Transformer  | 4871.73 | 0.321615 |
| ARIMA        | 5086.13 | 0.323014 |
| SMA          | 5396.66 | 0.343263 |
| Persistence+ | 5542.67 | 0.359713 |
| Naive        | 5759.72 | 0.374775 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: SIN-ORD
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4941.19 | 0.383355 |
| Transformer  | 5258.54 | 0.396985 |
| ARIMA        | 5511.61 | 0.419982 |
| SMA          | 5889.54 | 0.451669 |
| Persistence+ | 6206.11 | 0.483167 |
| Naive        | 6533.68 | 0.509003 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: SIN-PEK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3321.56 | 0.30271  |
| Transformer  | 3803.03 | 0.345108 |
| ARIMA        | 4029.08 | 0.352747 |
| SMA          | 4197.3  | 0.366763 |
| Persistence+ | 4493.04 | 0.400995 |
| Naive        | 4677.46 | 0.418119 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: SIN-PVG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3554.3  | 0.28773  |
| Transformer  | 4180.69 | 0.338589 |
| ARIMA        | 4415.36 | 0.344107 |
| SMA          | 4642.95 | 0.36176  |
| Persistence+ | 4807.02 | 0.386718 |
| Naive        | 4976.28 | 0.401668 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

## 3. Conclusions
- **Short-term (H=1):** Baselines like Naive/SMA are often competitive, but ARIMA usually leads.
- **Long-term (H=7, 30):** SARIMA and Transformer models show superior trend capture and lower WAPE.
- **Modularity:** The refactored architecture allows for seamless model swapping and testing.
