# -*- coding: utf-8 -*-
"""ModeloFinal.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DkETgSi4JAw9ldmODCaVMZU2mVMCf-yM

# **Predicción de homicidios por municipio**

### **Librerias para generación y visualización del dataset**
"""

# Importando librerias necesarias para la creación del dataset
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#Accede a Google Drive para importar los datos, los cuales provienen de una recopilación de bases de datos de indices de criminalidad en el triangulo norte
from google.colab import drive
drive.mount('/content/drive')

from google.colab import drive
drive.mount('/content/drive')

"""## **1. Recopilación de datos**
Los datos han sido extraidos de un archivo CSV recuperados de una [recopilación de Bases de Datos sobre indicadores de criminalidad y justicia en el triángulo norte](https://www.aas.jjay.cuny.edu/single-post/base-de-datos?fbclid=IwAR3Itx49fRZJoazPUPWYLpASA3bag7UjRUCzey4pvtec5O9mjdwG9QLboUE), a la cual se puede acceder en el enlace.

**Referencia**: Academy for Security Analysis, John Jay College of Criminal Justice. (2020). *Recopilación de Bases de Datos sobre indicadores de criminalidad y justicia en El Salvador, Guatemala y Honduras*.

Por ser información pública también ha sido anexado para facilitar su consulta.
"""

#Importando datos de CSV
#Referencia: Academy for Security Analysis, John Jay College of Criminal Justice. (2020). Recopilación de Bases de Datos sobre indicadores de criminalidad y justicia en El Salvador, Guatemala y Honduras.
df = pd.read_csv("drive/My Drive/IMLHom.csv")
print(len(df))
df.head()

"""## **2. Limpieza de datos**
Se procede a eliminar las columnas de dataset que son innecesarias para el modelo, así como a modificar los tipos de datos del mismo.
También se calcula el total de homicidios por año en cada municipio y se agrega esa nueva columna al dataset y finalmente se categorizan los nombres de los municipios.
"""

#Modifica el df a solo homicidios con los 4 tipos de armas que tenian más registros: ARMA DE FUEGO o ASF X ESTRANGULACION o OBJETO CONTUNDENTE o CORTOCONTUNDENTE
df = df[df.Tipo_Arma.str.contains('ARMA DE FUEGO|ASF X ESTRANGULACION|OBJETO CONTUNDENTE|CORTOCONTUNDENTE', regex=True)]
print(len(df))

#Eliminamos las columnas innecesarias
df = df.drop(['NoTotal', 'N', 'Mes', 'Fecha', 'Fecha_Completa', 'Dia','Hora', 'Rango_Horario', 'Departamento', 'Codigo_Departamento', 'Codigo_Municipio', 'Rango_Edad', 'Clasificacion_Arma', 'Edad', 'Sexo', 'Tipo_Arma'], axis=1)
df.head()

#Parseamos los tipos de datos
df = df.convert_dtypes()
df.info()

#Creamos una copia d la columna año para hacer el count()
df["AñoAux"] = df["Año"]

#Guardamos el df agrupado para luego asignar los totales a cada fila del df
df_g = df.groupby(['Municipio', 'Año']).count()

#Creamos la columna de total y la asignamos al df
totalArray = []
for municipio, año in zip(df["Municipio"], df["Año"]):
  totalArray.append(df_g.loc[municipio,año].AñoAux)

totalValues = pd.Series(totalArray)
df['Total'] = totalValues.values
df.head()

#Elimina la columna auxiliar
df.drop(['AñoAux'], axis = 1, inplace=True)
df.head()

#Covierte la columna municipio a tipo categoria
df["Municipio"] = df["Municipio"].astype('category')
df.dtypes

#Mapea el df asignando el codigo a los municipios que le corresponde
df["Municipio_encode"] = df["Municipio"].cat.codes
df.head(25)

#Crea un diccionario donde relaciona los codigos de la categorias con el nombre del municipio
municipiosDict = dict(zip(df['Municipio'].cat.codes, df['Municipio']))
print(municipiosDict)

#Eliminamos la columna municipio para el df final
final_df = df.drop(['Municipio'], axis = 1, inplace=False)
final_df.head()

"""## **3. Gráfico de totales por año.**
Se grafica la nube de puntos que tenemos en el dataset, donde se puede percibir que hay una gran variabilidad entre los datos, y que probablemente no sigan ningún tipo de tendencia.
"""

# Graficamos el total de homicidios por año para evaluar la 'tendencia'
final_df.plot(x ='Año', y='Total', kind = 'scatter')
plt.show()

"""## **4. Modelo de predicción de cantidad de homicidos**
El objetivo del modelo es determinar si a través de un año y municipio es posible encontrar un patrón o relación histórica con las cantidad (total) de homicidios en el mismo.
"""

#Definimos las variables x e y, dado un año y municipio se busca predecir cuandos homicidios habran
x = final_df[['Año', 'Municipio_encode']]
y = final_df[['Total']]

#Separamos el data set en 80% train y 20% test
from sklearn.model_selection import  train_test_split
x_train, x_test, y_train, y_test = train_test_split(x,y, test_size=0.2, random_state=42)

"""#### **Epsilon-Support Vector Regression con kernel Radial basis function (rbf)**"""

#Aplicamos el algoritmo de Epsilon-Support Vector Regression
from sklearn.svm import SVR

svr_rbf = SVR(kernel='rbf', C=100, gamma=0.1, epsilon=.1)
svr_rbf.fit(x_train,y_train.values.ravel())

y_pred_rbf = svr_rbf.predict(x_test)

"""Se obtiene un coeficiente de correlación ($R^2$) de 92.26% al entrenar el modelo y de un 91.92% al predecir los valores de $y$ comparado con los valores reales del dataset."""

#Obtenemos el coeficiente de determinacion para evaluar cuanto se ajusta el modelo
from sklearn.metrics import r2_score

r2_score_train = svr_rbf.score(x_train,y_train)
print('R^2 train: '+str(r2_score_train))

r2_score_test = r2_score(y_test,y_pred_rbf)
print('R^2 test: '+str(r2_score_test))

"""### **Guardar el modelo**"""

#Guardamos el modelo para que este persista
import joblib

filename = 'modelo_rbf.pkl'
joblib.dump(svr_rbf, filename)

#Cargamos el modelo guardado y verificamos su correcto funcionamiento
loaded_model = joblib.load(filename)
y_load = loaded_model.predict(x_test)

print(r2_score(y_test, y_load))