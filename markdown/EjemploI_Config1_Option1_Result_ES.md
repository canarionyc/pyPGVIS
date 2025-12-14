# Optimización de Sistema Energético Híbrido: FV + Biomasa

Este informe detalla el análisis y la optimización de un sistema energético híbrido que combina una instalación solar fotovoltaica (FV) con una caldera de biomasa. El objetivo es encontrar el tamaño óptimo del sistema FV que minimice el coste energético anual total para una instalación con necesidades significativas de calefacción, agua caliente sanitaria (ACS) y refrigeración.

---

## 1. Datos Energéticos Mensuales

La siguiente tabla resume el perfil energético mensual de la instalación, incluyendo la demanda térmica (Calefacción y ACS), la demanda de refrigeración y el recurso solar específico del emplazamiento.

| Mes | Demanda de Calefacción (kWh) | Demanda de ACS (kWh) | Demanda de Refrigeración (kWh) | Irradiación Solar (kWh/m²/mes) | Generación FV (kWh/kWp/mes) |
|:---   |---:|---:|---:|---:|---:|
| Ene   | 647.0 | 100.5 | 0.0 | 126.74 | 108.17 |
| Feb   | 487.0 | 89.5  | 0.0 | 132.68 | 112.17 |
| Mar   | 368.5 | 99.9  | 0.0 | 163.68 | 135.63 |
| Abr   | 202.3 | 90.5  | 0.0 | 162.94 | 131.25 |
| May   | 86.0  | 91.1  | 0.0 | 174.08 | 137.49 |
| Jun   | 0.0   | 81.3  | 16.4 | 178.35 | 136.68 |
| Jul   | 0.0   | 83.7  | 108.2 | 203.97 | 153.24 |
| Ago   | 0.0   | 83.3  | 99.3 | 198.07 | 149.91 |
| Sep   | 0.0   | 83.4  | 46.6 | 174.07 | 135.56 |
| Oct   | 86.0  | 90.8  | 0.0 | 162.10 | 130.30 |
| Nov   | 398.3 | 95.1  | 0.0 | 124.49 | 104.66 |
| Dic   | 658.9 | 103.0 | 0.0 | 126.10 | 107.09 |
| **Total** | **2,934.0** | **1,091.6** | **270.5** | | **1,542.15** |

*Nota: La Generación FV (`E_m`) es la producción eléctrica mensual estimada para un sistema de 1 kWp, teniendo en cuenta la eficiencia del panel y las pérdidas del sistema.*

---

## 2. Parámetros y Supuestos del Sistema

La optimización se basó en los siguientes parámetros técnicos y financieros.

### Hardware y Rendimiento del Sistema
| Parámetro | Valor | Descripción |
|:---|:---|:---|
| **Inclinación Panel FV** | 45° | Ángulo de inclinación de los paneles solares. |
| **Azimut Panel FV** | 180° | Los paneles están orientados al Sur para un rendimiento óptimo en el Hemisferio Norte. |
| **COP Bomba de Calor** | 3.5 | Se asume un Coeficiente de Rendimiento de 3.5 para convertir electricidad en calor. |
| **EER Aire Acondicionado** | 3.5 | Se asume un Ratio de Eficiencia Energética de 3.5 para convertir electricidad en frío. |

### Factores Económicos y de Coste
| Parámetro | Valor | Descripción |
|:---|:---|:---|
| **Coste Sistema FV Instalado** | 1.500 € / kWp | Coste todo incluido (paneles, inversor, montaje y mano de obra). |
| **Precio Pellet Biomasa** | 0.09 € / kWh | Coste de la energía térmica generada por la caldera de biomasa. |
| **Precio Importación Electricidad** | 0.16 € / kWh | Precio medio de compra de electricidad de la red. |
| **Precio Exportación Electricidad** | 0.02 € / kWh | Precio recibido por la venta de excedentes de electricidad FV a la red. |
| **Tasa de Interés Préstamo** | 6.0% | Tasa de interés anual para la financiación del sistema FV. |
| **Plazo del Préstamo** | 15 años | Período sobre el cual se anualiza la inversión del sistema FV. |

---
![optimal_monthly_energy_balance.png](../output/optimal_monthly_energy_balance.png)

## 3. Lógica de Cascada Energética y Optimización

Para encontrar la solución más rentable, se realizó una optimización. El modelo simula diferentes tamaños de sistemas FV y calcula el coste energético anual total para cada uno. La simulación utiliza una lógica de "cascada" para asignar la electricidad solar generada de la manera más valiosa.

El proceso mensual para el modelo es el siguiente:

1.  **Generación FV:** Se calcula la electricidad total generada por el sistema FV para el mes.
2.  **Cubrir Demanda de Refrigeración:** La electricidad generada se utiliza primero para alimentar el sistema de aire acondicionado y cubrir la demanda de refrigeración. Si la generación FV es insuficiente, el modelo comprará la electricidad restante de la red al precio de importación.
3.  **Cubrir Demanda de Calefacción y ACS:** Cualquier electricidad restante después de la refrigeración se utiliza para alimentar la bomba de calor y satisfacer la demanda de calefacción y ACS.
4.  **Activar Caldera de Biomasa:** Si la bomba de calor alimentada por FV no puede cubrir toda la demanda de calefacción y ACS, se activa la caldera de biomasa para proporcionar la energía térmica restante.
5.  **Vender Excedente de Electricidad:** Si queda algún excedente de electricidad después de cubrir todas las demandas de calefacción y refrigeración, se vende a la red al precio de exportación, generando ingresos.

El **objetivo de la optimización** es encontrar el tamaño del sistema FV donde la suma de todos estos costes (inversión anualizada FV + combustible de biomasa + importaciones de la red) menos los ingresos por exportaciones a la red, sea mínima. Esto representa la configuración económicamente más ventajosa a largo plazo.

Los resultados de esta optimización se presentan en los gráficos generados, que identifican el tamaño óptimo del sistema y visualizan los flujos de energía correspondientes.

![optimization_savings_vs_kwp_advanced.png](../output/optimization_savings_vs_kwp_advanced.png)

---


## 4. Validación del Hardware Seleccionado

La optimización identificó un tamaño de sistema ideal de **1.0 kWp**. Esto se puede implementar perfectamente utilizando **dos (2) paneles solares N-Type TOPCon 500W de Tensite**. Se revisaron las especificaciones técnicas de este panel específico para validar los supuestos de rendimiento utilizados en la simulación.

### Datos Técnicos del Panel (STC)
| Parámetro | Valor |
|:---|:---|
| **Potencia Máxima (Pmax)** | 500W (±3%) |
| **Eficiencia del Módulo** | 22.25% |
| **Coef. de Temperatura (Pmax)** | **-0.30% / °C** |

### Análisis y Conclusión

El parámetro más crítico para el rendimiento en condiciones reales es el **Coeficiente de Temperatura de Pmax**. El panel seleccionado tiene un coeficiente de **-0.30% / °C**, que es significativamente mejor que el promedio de la industria para paneles convencionales (aprox. -0.40% / °C).

La simulación de PVGIS utilizada para estimar la generación de energía asumió una pérdida total del sistema del **14%**. Esta es una cifra estándar y conservadora que tiene en cuenta todas las fuentes de ineficiencia del mundo real, siendo las pérdidas relacionadas con la temperatura el componente más importante.

Dada la superior resistencia al calor de los paneles N-Type TOPCon seleccionados, sus pérdidas totales reales del sistema probablemente estarán más cerca del **10-12%**.

**Veredicto:** La suposición de pérdidas del 14% en nuestro modelo es conservadora. El hardware elegido es de alta calidad y es muy probable que su rendimiento sea **mejor** que el predicho por la simulación. Esto proporciona un alto grado de confianza en que la generación de energía y los ahorros financieros calculados son un objetivo realista y alcanzable.
