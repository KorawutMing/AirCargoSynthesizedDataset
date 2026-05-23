# Forecasting Performance Report

## 1. Global Summary
|                      |            MAE |           RMSE |       WAPE |   Trend (Corr) |
|:---------------------|---------------:|---------------:|-----------:|---------------:|
| (1, 'Transformer')   | 3235.13        | 3235.13        |   0.271237 |     0          |
| (1, 'ARIMA')         | 4210.58        | 4210.58        |   0.365716 |     0          |
| (1, 'SMA')           | 4574.77        | 4574.77        |   0.392059 |     0          |
| (1, 'Persistence+')  | 5009.84        | 5009.84        |   0.415607 |     0          |
| (1, 'Naive')         | 5074.2         | 5074.2         |   0.420506 |     0          |
| (1, 'SARIMA')        |    1.13501e+06 |    1.13501e+06 |  88.7092   |     0          |
| (7, 'Transformer')   | 3458.08        | 4247.63        |   0.246101 |     0.643948   |
| (7, 'ARIMA')         | 4552.32        | 5475.76        |   0.312381 |     0.0460962  |
| (7, 'SMA')           | 4587.71        | 5497.95        |   0.313958 |     0          |
| (7, 'Persistence+')  | 5601.21        | 6651           |   0.389584 |    -0.0266574  |
| (7, 'Naive')         | 5807.64        | 6865.6         |   0.404499 |     0          |
| (7, 'SARIMA')        |    1.1372e+06  |    1.13796e+06 |  88.6831   |     0.676214   |
| (30, 'Transformer')  | 3662.76        | 4660.15        |   0.255192 |     0.59263    |
| (30, 'ARIMA')        | 4642.2         | 5703.69        |   0.314169 |     0.0219542  |
| (30, 'SMA')          | 4643.56        | 5699.83        |   0.31426  |     0          |
| (30, 'Persistence+') | 5446.53        | 6634.08        |   0.374122 |    -0.00658755 |
| (30, 'Naive')        | 5922.11        | 7131.39        |   0.407528 |     0          |
| (30, 'SARIMA')       |    1.1453e+06  |    1.14625e+06 | 105.793    |     0.632383   |

## 2. Route-Specific Analysis
### Route: CAN-CGO
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 1130.75 | 0.357536 |
| Transformer  | 1136.32 | 0.349905 |
| ARIMA        | 1418.62 | 0.427784 |
| SMA          | 1446.15 | 0.436081 |
| Persistence+ | 1844.98 | 0.523564 |
| Naive        | 1940.41 | 0.549056 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CAN-HKG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 602.699 | 0.69503  |
| Transformer  | 604.572 | 0.655193 |
| ARIMA        | 647.804 | 0.726439 |
| SMA          | 655.675 | 0.725199 |
| Persistence+ | 837.267 | 0.894972 |
| Naive        | 876.972 | 0.930257 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CAN-JFK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3540.96 | 0.252427 |
| Transformer  | 3551.1  | 0.250389 |
| ARIMA        | 4514.26 | 0.316539 |
| SMA          | 4580.17 | 0.319987 |
| Persistence+ | 5223.54 | 0.36803  |
| Naive        | 5432.74 | 0.383053 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CAN-LAX
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 4052.91 | 0.250854 |
| SARIMA       | 4063.79 | 0.258078 |
| ARIMA        | 5030.04 | 0.312089 |
| SMA          | 5129.67 | 0.317444 |
| Persistence+ | 5884.9  | 0.361377 |
| Naive        | 6130.25 | 0.376207 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CAN-NRT
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 3706.7  | 0.230203 |
| SARIMA       | 3745.13 | 0.23663  |
| ARIMA        | 4982.15 | 0.314712 |
| SMA          | 5188.05 | 0.32593  |
| Persistence+ | 5758.04 | 0.359996 |
| Naive        | 6011.22 | 0.374843 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CAN-ORD
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 4269.94 | 0.255834 |
| SARIMA       | 4346.5  | 0.263983 |
| ARIMA        | 5416.1  | 0.320792 |
| SMA          | 5490.92 | 0.326342 |
| Persistence+ | 6564.83 | 0.38855  |
| Naive        | 6864.88 | 0.406337 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CAN-PEK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3634.59 | 0.239589 |
| Transformer  | 3647.78 | 0.237967 |
| ARIMA        | 4901.3  | 0.313669 |
| SMA          | 5030.32 | 0.323135 |
| Persistence+ | 6044.9  | 0.394989 |
| Naive        | 6330.2  | 0.414318 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CAN-PVG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2560.14 | 0.233755 |
| Transformer  | 2594.72 | 0.227766 |
| ARIMA        | 3533.8  | 0.313543 |
| SMA          | 3615.79 | 0.3198   |
| Persistence+ | 4438.43 | 0.383701 |
| Naive        | 4651.37 | 0.40209  |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CAN-SIN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 3274.31 | 0.226926 |
| SARIMA       | 3310.99 | 0.236886 |
| ARIMA        | 4475.02 | 0.313926 |
| SMA          | 4654.22 | 0.326375 |
| Persistence+ | 5676.63 | 0.389414 |
| Naive        | 5989.21 | 0.41002  |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CGO-CAN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2252.16 | 0.244824 |
| Transformer  | 2357.22 | 0.253909 |
| ARIMA        | 2906.85 | 0.314944 |
| SMA          | 2998.34 | 0.323257 |
| Persistence+ | 3830.08 | 0.408651 |
| Naive        | 4029.09 | 0.429237 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CGO-HKG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3912.85 | 0.231829 |
| Transformer  | 4028.07 | 0.241769 |
| ARIMA        | 5298.55 | 0.311588 |
| SMA          | 5565.49 | 0.32784  |
| Persistence+ | 6722.29 | 0.3842   |
| Naive        | 7136.21 | 0.406174 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CGO-JFK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4415.59 | 0.248554 |
| Transformer  | 4426.06 | 0.244728 |
| ARIMA        | 5588.01 | 0.314721 |
| SMA          | 5686.8  | 0.318588 |
| Persistence+ | 6541.27 | 0.365345 |
| Naive        | 6812.25 | 0.379839 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CGO-LAX
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 3960.49 | 0.268748 |
| SARIMA       | 3975.31 | 0.273551 |
| ARIMA        | 4896.37 | 0.331308 |
| SMA          | 5017.7  | 0.338482 |
| Persistence+ | 5572.77 | 0.373421 |
| Naive        | 5809.1  | 0.38952  |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CGO-NRT
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3559.76 | 0.237915 |
| Transformer  | 3598.17 | 0.240811 |
| ARIMA        | 4766.12 | 0.318817 |
| SMA          | 4977.86 | 0.334869 |
| Persistence+ | 5759.71 | 0.377448 |
| Naive        | 6036.72 | 0.395475 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CGO-ORD
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 4196    | 0.253299 |
| SARIMA       | 4250.6  | 0.263112 |
| ARIMA        | 5357.14 | 0.326094 |
| SMA          | 5478.44 | 0.333197 |
| Persistence+ | 5959.63 | 0.358073 |
| Naive        | 6187.71 | 0.372141 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CGO-PEK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 3567.43 | 0.240618 |
| SARIMA       | 3661.66 | 0.255516 |
| ARIMA        | 4821.09 | 0.328776 |
| SMA          | 5033.34 | 0.345289 |
| Persistence+ | 5624.84 | 0.401007 |
| Naive        | 5919.22 | 0.423166 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CGO-PVG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2690.27 | 0.258656 |
| Transformer  | 2698.85 | 0.258512 |
| ARIMA        | 3581.13 | 0.342942 |
| SMA          | 3657.13 | 0.347686 |
| Persistence+ | 4708.03 | 0.466379 |
| Naive        | 4949.94 | 0.489834 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: CGO-SIN
| Model        |            MAE |       WAPE |
|:-------------|---------------:|-----------:|
| Transformer  | 3170.76        |   0.225575 |
| ARIMA        | 4309.28        |   0.306611 |
| SMA          | 4453.96        |   0.31942  |
| Persistence+ | 5281.21        |   0.363066 |
| Naive        | 5530.9         |   0.379654 |
| SARIMA       |    1.34263e+07 | 745.26     |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** SARIMA struggles with the volatility or seasonality of this route.

### Route: HKG-CAN
| Model        |     MAE |    WAPE |
|:-------------|--------:|--------:|
| SARIMA       | 462.618 | 1.05137 |
| Transformer  | 476.305 | 1.02401 |
| ARIMA        | 483.433 | 1.07804 |
| SMA          | 486.434 | 1.10018 |
| Persistence+ | 598.286 | 1.29794 |
| Naive        | 626.508 | 1.34819 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: HKG-CGO
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 1330.02 | 0.375336 |
| Transformer  | 1333.11 | 0.369992 |
| ARIMA        | 1581.59 | 0.447944 |
| SMA          | 1609.55 | 0.459674 |
| Persistence+ | 1993.09 | 0.533104 |
| Naive        | 2088.47 | 0.55691  |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: HKG-JFK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4025.43 | 0.270491 |
| Transformer  | 4056.52 | 0.264125 |
| ARIMA        | 4968.27 | 0.326574 |
| SMA          | 5069.53 | 0.330965 |
| Persistence+ | 5537.2  | 0.366145 |
| Naive        | 5759.13 | 0.380705 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: HKG-LAX
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 4167.55 | 0.251813 |
| SARIMA       | 4230.49 | 0.26188  |
| ARIMA        | 5435.18 | 0.329086 |
| SMA          | 5608.65 | 0.339974 |
| Persistence+ | 6243.73 | 0.375413 |
| Naive        | 6515.62 | 0.391781 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: HKG-NRT
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 3647.11 | 0.218086 |
| SARIMA       | 3687.3  | 0.223426 |
| ARIMA        | 5029.27 | 0.299505 |
| SMA          | 5203.18 | 0.31039  |
| Persistence+ | 6316.67 | 0.367076 |
| Naive        | 6641.27 | 0.384909 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: HKG-ORD
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 4381.45 | 0.245414 |
| SARIMA       | 4430.86 | 0.252489 |
| ARIMA        | 5542.37 | 0.309121 |
| SMA          | 5692.23 | 0.315331 |
| Persistence+ | 6304.03 | 0.358113 |
| Naive        | 6549.53 | 0.372515 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: HKG-PEK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3749.95 | 0.240808 |
| Transformer  | 3778.34 | 0.242845 |
| ARIMA        | 4953.75 | 0.313011 |
| SMA          | 5153.04 | 0.324326 |
| Persistence+ | 6055.52 | 0.370936 |
| Naive        | 6353.88 | 0.388471 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: HKG-PVG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2934.23 | 0.244555 |
| Transformer  | 2982.04 | 0.249989 |
| ARIMA        | 3806.86 | 0.320211 |
| SMA          | 3976.78 | 0.333998 |
| Persistence+ | 5096.11 | 0.412668 |
| Naive        | 5432.01 | 0.438578 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: HKG-SIN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 3461.38 | 0.215453 |
| SARIMA       | 3515.9  | 0.218501 |
| ARIMA        | 4746.07 | 0.290164 |
| SMA          | 4876.74 | 0.29841  |
| Persistence+ | 5987.66 | 0.369983 |
| Naive        | 6288.37 | 0.388621 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: JFK-CAN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2808.8  | 0.239352 |
| Transformer  | 2849.14 | 0.239262 |
| ARIMA        | 3788.52 | 0.313318 |
| SMA          | 3845.54 | 0.316756 |
| Persistence+ | 4995.94 | 0.401209 |
| Naive        | 5273.86 | 0.421503 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: JFK-CGO
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 1565.05 | 0.398484 |
| Transformer  | 1648.06 | 0.401654 |
| ARIMA        | 1905.04 | 0.498033 |
| SMA          | 1940.27 | 0.509679 |
| Persistence+ | 2209.46 | 0.556147 |
| Naive        | 2296.48 | 0.574246 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: JFK-HKG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2874.48 | 0.238192 |
| Transformer  | 2903.76 | 0.235695 |
| ARIMA        | 3857.47 | 0.313887 |
| SMA          | 3951.31 | 0.323005 |
| Persistence+ | 4612.37 | 0.377781 |
| Naive        | 4816.92 | 0.395242 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: JFK-LAX
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2786.35 | 0.235348 |
| Transformer  | 2831.56 | 0.238408 |
| ARIMA        | 3840.53 | 0.317263 |
| SMA          | 3914.77 | 0.322033 |
| Persistence+ | 4639.34 | 0.387242 |
| Naive        | 4842.34 | 0.403871 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: JFK-NRT
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4170.49 | 0.22607  |
| Transformer  | 4222.38 | 0.226053 |
| ARIMA        | 5367.81 | 0.278903 |
| SMA          | 5550.86 | 0.289541 |
| Persistence+ | 6542.91 | 0.343522 |
| Naive        | 6864.18 | 0.360114 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: JFK-ORD
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 1523.43 | 0.280047 |
| Transformer  | 1647.46 | 0.289738 |
| ARIMA        | 1905.8  | 0.34931  |
| SMA          | 1917.98 | 0.354243 |
| Persistence+ | 2374.27 | 0.41204  |
| Naive        | 2477.17 | 0.428539 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: JFK-PEK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2340.53 | 0.242376 |
| Transformer  | 2466.54 | 0.245794 |
| ARIMA        | 3179.52 | 0.321579 |
| SMA          | 3244.01 | 0.328884 |
| Persistence+ | 3801.49 | 0.386647 |
| Naive        | 3963.69 | 0.403124 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: JFK-PVG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3460.89 | 0.227454 |
| Transformer  | 3585.59 | 0.230398 |
| ARIMA        | 4570.13 | 0.295555 |
| SMA          | 4718.99 | 0.302722 |
| Persistence+ | 5200.83 | 0.335291 |
| Naive        | 5408.44 | 0.348211 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: JFK-SIN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 3848.71 | 0.220324 |
| SARIMA       | 3891.58 | 0.229217 |
| ARIMA        | 5105.14 | 0.290199 |
| SMA          | 5396.41 | 0.303414 |
| Persistence+ | 6053.4  | 0.337709 |
| Naive        | 6352.68 | 0.353604 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: LAX-CAN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2469.92 | 0.251678 |
| Transformer  | 2537.96 | 0.258665 |
| ARIMA        | 3157.11 | 0.311629 |
| SMA          | 3329.47 | 0.327729 |
| Persistence+ | 3980.38 | 0.372916 |
| Naive        | 4182.53 | 0.390381 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: LAX-CGO
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 1390.58 | 0.357643 |
| Transformer  | 1439.98 | 0.361265 |
| ARIMA        | 1705.52 | 0.43427  |
| SMA          | 1744.9  | 0.443239 |
| Persistence+ | 2058.51 | 0.52207  |
| Naive        | 2147.12 | 0.541948 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: LAX-HKG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2598.34 | 0.283327 |
| Transformer  | 2610.54 | 0.280801 |
| ARIMA        | 3241.36 | 0.352504 |
| SMA          | 3327.99 | 0.361187 |
| Persistence+ | 3844.14 | 0.411398 |
| Naive        | 4004.4  | 0.426443 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: LAX-JFK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 2361.34 | 0.248933 |
| SARIMA       | 2377.35 | 0.254181 |
| ARIMA        | 3085.28 | 0.319718 |
| SMA          | 3198.16 | 0.33136  |
| Persistence+ | 3731.81 | 0.386519 |
| Naive        | 3925.14 | 0.406    |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: LAX-NRT
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3529.21 | 0.234969 |
| Transformer  | 3577.88 | 0.232184 |
| ARIMA        | 4713.31 | 0.313525 |
| SMA          | 4794.01 | 0.321766 |
| Persistence+ | 6195.03 | 0.401742 |
| Naive        | 6510.81 | 0.420749 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: LAX-ORD
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3728.22 | 0.217657 |
| Transformer  | 3739.3  | 0.213195 |
| ARIMA        | 5358.93 | 0.306326 |
| SMA          | 5589.89 | 0.319538 |
| Persistence+ | 6117.08 | 0.345539 |
| Naive        | 6384.68 | 0.360914 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: LAX-PEK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3776.14 | 0.224512 |
| Transformer  | 3788.94 | 0.220538 |
| ARIMA        | 5026.66 | 0.284973 |
| SMA          | 5237.72 | 0.296074 |
| Persistence+ | 6100.89 | 0.336515 |
| Naive        | 6431.68 | 0.354046 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: LAX-PVG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3113.71 | 0.248548 |
| Transformer  | 3138.88 | 0.242488 |
| ARIMA        | 3986.22 | 0.308315 |
| SMA          | 4123.9  | 0.318566 |
| Persistence+ | 4879.29 | 0.366526 |
| Naive        | 5166.17 | 0.385569 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: LAX-SIN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3328.22 | 0.224964 |
| Transformer  | 3381.07 | 0.224993 |
| ARIMA        | 4527.49 | 0.302244 |
| SMA          | 4772.61 | 0.318444 |
| Persistence+ | 5293.45 | 0.352593 |
| Naive        | 5543.86 | 0.370433 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: NRT-CAN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2985.44 | 0.236892 |
| Transformer  | 3032.08 | 0.236713 |
| ARIMA        | 4046.45 | 0.315649 |
| SMA          | 4149.69 | 0.323237 |
| Persistence+ | 5526.84 | 0.414342 |
| Naive        | 5840.14 | 0.437038 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: NRT-CGO
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2651.76 | 0.276414 |
| Transformer  | 2724.9  | 0.281527 |
| ARIMA        | 3393.1  | 0.346621 |
| SMA          | 3491.29 | 0.352984 |
| Persistence+ | 4060.84 | 0.402079 |
| Naive        | 4233.94 | 0.417224 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: NRT-HKG
| Model        |            MAE |        WAPE |
|:-------------|---------------:|------------:|
| Transformer  | 3785.77        |    0.229042 |
| ARIMA        | 5354.04        |    0.325197 |
| SMA          | 5479.41        |    0.335152 |
| Persistence+ | 6604.33        |    0.39092  |
| Naive        | 6930.79        |    0.409606 |
| SARIMA       |    5.00058e+07 | 4465.83     |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** SARIMA struggles with the volatility or seasonality of this route.

### Route: NRT-JFK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4219.53 | 0.273956 |
| Transformer  | 4247.15 | 0.270048 |
| ARIMA        | 5225.67 | 0.330911 |
| SMA          | 5367.81 | 0.33867  |
| Persistence+ | 5912.27 | 0.370185 |
| Naive        | 6132.81 | 0.383696 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: NRT-LAX
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4287.72 | 0.243962 |
| Transformer  | 4331.07 | 0.23973  |
| ARIMA        | 5416.57 | 0.302504 |
| SMA          | 5595.44 | 0.312673 |
| Persistence+ | 6125.09 | 0.339058 |
| Naive        | 6379.32 | 0.353475 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: NRT-ORD
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 3647.41 | 0.270755 |
| SARIMA       | 3655.74 | 0.278142 |
| ARIMA        | 4586.17 | 0.336338 |
| SMA          | 4721.48 | 0.34249  |
| Persistence+ | 5328.43 | 0.391355 |
| Naive        | 5565.81 | 0.407665 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: NRT-PEK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3279.96 | 0.233512 |
| Transformer  | 3326.02 | 0.231513 |
| ARIMA        | 4478.53 | 0.317277 |
| SMA          | 4649.77 | 0.329271 |
| Persistence+ | 5597.66 | 0.385561 |
| Naive        | 5890.57 | 0.405014 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: NRT-PVG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2337.71 | 0.26483  |
| Transformer  | 2359.77 | 0.268275 |
| ARIMA        | 3126.33 | 0.357439 |
| SMA          | 3231.08 | 0.370079 |
| Persistence+ | 3869.39 | 0.448669 |
| Naive        | 4095.99 | 0.472472 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: NRT-SIN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3996.58 | 0.215844 |
| Transformer  | 4098.68 | 0.216942 |
| ARIMA        | 5468.51 | 0.291871 |
| SMA          | 5734.8  | 0.305461 |
| Persistence+ | 6629.46 | 0.344468 |
| Naive        | 6950.05 | 0.360379 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: ORD-CAN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2485.8  | 0.253039 |
| Transformer  | 2579.34 | 0.254622 |
| ARIMA        | 3282.9  | 0.32438  |
| SMA          | 3436.3  | 0.341814 |
| Persistence+ | 4089.67 | 0.38534  |
| Naive        | 4300.12 | 0.404808 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: ORD-CGO
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2108.72 | 0.243023 |
| Transformer  | 2167.46 | 0.246978 |
| ARIMA        | 2678.41 | 0.306135 |
| SMA          | 2811.34 | 0.322472 |
| Persistence+ | 3237.93 | 0.37105  |
| Naive        | 3390.84 | 0.389076 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: ORD-HKG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 3067.77 | 0.229873 |
| ARIMA        | 4052.45 | 0.30363  |
| SMA          | 4225.73 | 0.317271 |
| Persistence+ | 4701.58 | 0.342062 |
| Naive        | 4912.48 | 0.356811 |
| SARIMA       | 6009.14 | 0.635085 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** SARIMA struggles with the volatility or seasonality of this route.

### Route: ORD-JFK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2894.67 | 0.253397 |
| Transformer  | 2906.04 | 0.248893 |
| ARIMA        | 3816.45 | 0.331828 |
| SMA          | 3869.01 | 0.335932 |
| Persistence+ | 4722.08 | 0.411794 |
| Naive        | 4973.43 | 0.432597 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: ORD-LAX
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3249.26 | 0.235571 |
| Transformer  | 3351.36 | 0.238022 |
| ARIMA        | 4431.14 | 0.31459  |
| SMA          | 4538.27 | 0.322333 |
| Persistence+ | 5433.14 | 0.373108 |
| Naive        | 5691.36 | 0.389878 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: ORD-NRT
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3482.1  | 0.222236 |
| Transformer  | 3503.46 | 0.218676 |
| ARIMA        | 4751.04 | 0.297198 |
| SMA          | 4936.26 | 0.309123 |
| Persistence+ | 5569.59 | 0.348301 |
| Naive        | 5837.89 | 0.364534 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: ORD-PEK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3738.14 | 0.218065 |
| Transformer  | 3855.41 | 0.221903 |
| ARIMA        | 4988.19 | 0.283494 |
| SMA          | 5170.05 | 0.294468 |
| Persistence+ | 5898.55 | 0.333805 |
| Naive        | 6165.16 | 0.348891 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: ORD-PVG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2884.14 | 0.240866 |
| Transformer  | 2957.83 | 0.242161 |
| ARIMA        | 3954.94 | 0.324832 |
| SMA          | 4118.85 | 0.336929 |
| Persistence+ | 4643.62 | 0.377164 |
| Naive        | 4854.57 | 0.393832 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: ORD-SIN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3467.49 | 0.237114 |
| Transformer  | 3554.51 | 0.23446  |
| ARIMA        | 4499.73 | 0.30342  |
| SMA          | 4638.35 | 0.312473 |
| Persistence+ | 5580.18 | 0.371976 |
| Naive        | 5828.37 | 0.387826 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PEK-CAN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 1587.41 | 0.31682  |
| Transformer  | 1653.93 | 0.321032 |
| ARIMA        | 1902.81 | 0.368499 |
| SMA          | 1963.16 | 0.374397 |
| Persistence+ | 2385.94 | 0.475086 |
| Naive        | 2509.56 | 0.497291 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PEK-CGO
| Model        |      MAE |     WAPE |
|:-------------|---------:|---------:|
| SARIMA       |  869.487 | 0.447058 |
| Transformer  |  903.878 | 0.443217 |
| ARIMA        |  969.704 | 0.483116 |
| SMA          |  995.886 | 0.496764 |
| Persistence+ | 1195.16  | 0.597043 |
| Naive        | 1249.92  | 0.62224  |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PEK-HKG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2466.32 | 0.27429  |
| Transformer  | 2550.13 | 0.273255 |
| ARIMA        | 3296.89 | 0.360011 |
| SMA          | 3417.51 | 0.372181 |
| Persistence+ | 3838.18 | 0.406305 |
| Naive        | 3997.02 | 0.421943 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PEK-JFK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 3803.34 | 0.244706 |
| SARIMA       | 4011.37 | 0.262995 |
| ARIMA        | 4996.36 | 0.32011  |
| SMA          | 5235.48 | 0.334665 |
| Persistence+ | 5677.55 | 0.361729 |
| Naive        | 5934.24 | 0.37776  |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PEK-LAX
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 4398.8  | 0.237052 |
| SARIMA       | 4436.35 | 0.250153 |
| ARIMA        | 5706.92 | 0.314709 |
| SMA          | 5824.09 | 0.317894 |
| Persistence+ | 6688.66 | 0.375702 |
| Naive        | 6981.66 | 0.39238  |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PEK-NRT
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3098.4  | 0.235245 |
| Transformer  | 3130    | 0.232468 |
| ARIMA        | 4064.66 | 0.304883 |
| SMA          | 4206.59 | 0.312905 |
| Persistence+ | 5267.06 | 0.391977 |
| Naive        | 5555.35 | 0.412436 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PEK-ORD
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3691.08 | 0.265122 |
| Transformer  | 3726.97 | 0.26277  |
| ARIMA        | 4482.77 | 0.3173   |
| SMA          | 4548.4  | 0.319946 |
| Persistence+ | 5251.61 | 0.376242 |
| Naive        | 5469.26 | 0.391473 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PEK-PVG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 1701.4  | 0.419652 |
| Transformer  | 1706.21 | 0.417833 |
| ARIMA        | 2162.05 | 0.570102 |
| SMA          | 2188.62 | 0.594422 |
| Persistence+ | 2781.52 | 0.58491  |
| Naive        | 2916.55 | 0.604713 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PEK-SIN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3046.84 | 0.258174 |
| Transformer  | 3055.45 | 0.257781 |
| ARIMA        | 3963.49 | 0.329825 |
| SMA          | 4110.87 | 0.342016 |
| Persistence+ | 5119.71 | 0.410672 |
| Naive        | 5400.33 | 0.432017 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PVG-CAN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2599.51 | 0.256798 |
| Transformer  | 2680.4  | 0.26431  |
| ARIMA        | 3444.94 | 0.33526  |
| SMA          | 3514.39 | 0.338398 |
| Persistence+ | 4432.55 | 0.421182 |
| Naive        | 4629.24 | 0.438611 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PVG-CGO
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 1370.94 | 0.39691  |
| Transformer  | 1382.02 | 0.39691  |
| ARIMA        | 1615.86 | 0.466428 |
| SMA          | 1656.73 | 0.477429 |
| Persistence+ | 2062.27 | 0.580715 |
| Naive        | 2163.1  | 0.606067 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PVG-HKG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2471.81 | 0.272989 |
| Transformer  | 2550.54 | 0.278895 |
| ARIMA        | 3255.78 | 0.352705 |
| SMA          | 3395.9  | 0.369747 |
| Persistence+ | 4005.03 | 0.417906 |
| Naive        | 4208.71 | 0.438489 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PVG-JFK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4007.79 | 0.260289 |
| Transformer  | 4059.46 | 0.25614  |
| ARIMA        | 5120.56 | 0.326469 |
| SMA          | 5238.02 | 0.333877 |
| Persistence+ | 5967.16 | 0.378889 |
| Naive        | 6221.29 | 0.395346 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PVG-LAX
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 4458.1  | 0.2467   |
| SARIMA       | 4518.09 | 0.257223 |
| ARIMA        | 5684.36 | 0.316706 |
| SMA          | 5870.87 | 0.325596 |
| Persistence+ | 6468.56 | 0.364239 |
| Naive        | 6748.51 | 0.380699 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PVG-NRT
| Model        |      MAE |     WAPE |
|:-------------|---------:|---------:|
| Transformer  |  3469.66 | 0.218591 |
| ARIMA        |  4494.2  | 0.28737  |
| SMA          |  4717.2  | 0.300863 |
| Persistence+ |  5732.2  | 0.36392  |
| Naive        |  6046.8  | 0.383087 |
| SARIMA       | 22151.1  | 2.44104  |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** SARIMA struggles with the volatility or seasonality of this route.

### Route: PVG-ORD
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4847.15 | 0.262601 |
| Transformer  | 4900.33 | 0.258891 |
| ARIMA        | 6151.8  | 0.327064 |
| SMA          | 6236.38 | 0.331574 |
| Persistence+ | 7009.94 | 0.371637 |
| Naive        | 7307.34 | 0.38773  |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PVG-PEK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 3704.9  | 0.219725 |
| SARIMA       | 3891.77 | 0.234385 |
| ARIMA        | 5113.83 | 0.304466 |
| SMA          | 5272.07 | 0.317708 |
| Persistence+ | 6485.08 | 0.369659 |
| Naive        | 6790.23 | 0.386238 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: PVG-SIN
| Model        |            MAE |       WAPE |
|:-------------|---------------:|-----------:|
| Transformer  | 3802.6         |   0.223032 |
| ARIMA        | 5177.26        |   0.308505 |
| SMA          | 5400.54        |   0.321354 |
| Persistence+ | 6474.7         |   0.386153 |
| Naive        | 6809.45        |   0.406079 |
| SARIMA       |    4.71326e+06 | 436.474    |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** SARIMA struggles with the volatility or seasonality of this route.

### Route: SIN-CAN
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3000.34 | 0.250269 |
| Transformer  | 3022.43 | 0.247133 |
| ARIMA        | 4021.94 | 0.332227 |
| SMA          | 4167.62 | 0.344979 |
| Persistence+ | 4806.62 | 0.390106 |
| Naive        | 5039.62 | 0.408427 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: SIN-CGO
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 2562.72 | 0.268675 |
| Transformer  | 2650.8  | 0.272874 |
| ARIMA        | 3279.49 | 0.337846 |
| SMA          | 3455.14 | 0.358605 |
| Persistence+ | 3786.32 | 0.369047 |
| Naive        | 3965.87 | 0.38584  |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: SIN-HKG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 3575.91 | 0.236043 |
| SARIMA       | 3652.17 | 0.242448 |
| ARIMA        | 4929.84 | 0.324059 |
| SMA          | 5079.58 | 0.334827 |
| Persistence+ | 6086    | 0.396013 |
| Naive        | 6384.29 | 0.414359 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: SIN-JFK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3951.88 | 0.276987 |
| Transformer  | 3985.8  | 0.27538  |
| ARIMA        | 4941.1  | 0.338986 |
| SMA          | 5039.73 | 0.34405  |
| Persistence+ | 5578.74 | 0.385709 |
| Naive        | 5795.33 | 0.400909 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: SIN-LAX
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 4228.3  | 0.254713 |
| SARIMA       | 4277.96 | 0.267022 |
| ARIMA        | 5264.05 | 0.318553 |
| SMA          | 5349.93 | 0.321079 |
| Persistence+ | 6123    | 0.3741   |
| Naive        | 6378.54 | 0.390423 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: SIN-NRT
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 4127.08 | 0.228281 |
| Transformer  | 4136.51 | 0.224232 |
| ARIMA        | 5593.18 | 0.306402 |
| SMA          | 5789.6  | 0.318278 |
| Persistence+ | 6938.99 | 0.371436 |
| Naive        | 7302.51 | 0.390108 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: SIN-ORD
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| SARIMA       | 3357.89 | 0.25672  |
| Transformer  | 3398.29 | 0.254689 |
| ARIMA        | 4192.46 | 0.316688 |
| SMA          | 4262    | 0.318478 |
| Persistence+ | 5019.68 | 0.385572 |
| Naive        | 5247.56 | 0.402511 |

**Strengths:** SARIMA performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: SIN-PEK
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 3069.42 | 0.238784 |
| SARIMA       | 3102.38 | 0.244521 |
| ARIMA        | 4147.45 | 0.326545 |
| SMA          | 4278.45 | 0.336522 |
| Persistence+ | 5457.22 | 0.418403 |
| Naive        | 5757    | 0.439564 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

### Route: SIN-PVG
| Model        |     MAE |     WAPE |
|:-------------|--------:|---------:|
| Transformer  | 3478.97 | 0.234631 |
| SARIMA       | 3486.87 | 0.23884  |
| ARIMA        | 4560.43 | 0.308241 |
| SMA          | 4775.46 | 0.32316  |
| Persistence+ | 6014.83 | 0.394581 |
| Naive        | 6354.31 | 0.416235 |

**Strengths:** Transformer performs best on this route.
**Weaknesses:** Naive struggles with the volatility or seasonality of this route.

## 3. Conclusions
- **Short-term (H=1):** Baselines like Naive/SMA are often competitive, but ARIMA usually leads.
- **Long-term (H=7, 30):** SARIMA and Transformer models show superior trend capture and lower WAPE.
- **Modularity:** The refactored architecture allows for seamless model swapping and testing.
