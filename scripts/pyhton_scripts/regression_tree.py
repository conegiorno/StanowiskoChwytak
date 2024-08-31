from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import medfilt

def print_err(x, x_aprox, name, type):
    print(f'{name} - {type}')
    err = abs(x - x_aprox)
    err_rel = abs(err/x) * 100
    print(f'Err bezwzględny max: {max(err)}')
    print(f'Err bezwzględny średni: {sum(err)/len(err)}')
    print(f'Err względny max: {max(err_rel)}%')
    print(f'Err względny średni: {sum(err_rel)/len(err_rel)}%')

def filter_df(df, window):
    df['RotSens1'] = medfilt(df['RotSens1'], window)
    df['RotSens2'] = medfilt(df['RotSens2'], window)
    df['PresSens1'] = medfilt(df['PresSens1'], window)
    df['PresSens2'] = medfilt(df['PresSens2'], window)
    df['CurrSens1'] = medfilt(df['CurrSens1'], window)
    df['CurrSens2'] = medfilt(df['CurrSens2'], window)
    df['ForceZ'] = medfilt(df['ForceZ'], window)
    return df

# put directory to your datasets here
cylinder_dir = 'datasets/two_finger_grasp_cylinder.csv'
sphere_dir = 'datasets/two_finger_grasp_sphere.csv'

df_cylinder = pd.DataFrame(pd.read_csv(cylinder_dir))
df_sphere = pd.DataFrame(pd.read_csv(sphere_dir))

df_cylinder = filter_df(df_cylinder, 5)
df_sphere = filter_df(df_sphere, 5)

df_cl = df_cylinder.loc[:6000]
df_sp = df_sphere.loc[:6000]

df_cylinder = df_cylinder.loc[6000:]
df_sphere = df_sphere.loc[6000:]

df = pd.concat([df_cylinder, df_sphere], ignore_index=True)


df_data = df[['RotSens1','RotSens2','PresSens1','PresSens2','CurrSens1','CurrSens2']]
df_target = -df['ForceZ']

df_cl_data = df_cl[['RotSens1','RotSens2','PresSens1','PresSens2','CurrSens1','CurrSens2']]
df_cl_target = -df_cl['ForceZ']

df_sp_data = df_sp[['RotSens1','RotSens2','PresSens1','PresSens2','CurrSens1','CurrSens2']]
df_sp_target = -df_sp['ForceZ']


X_train, X_test, y_train, y_test = train_test_split(df_data, df_target, test_size=0.2, random_state=42)

regressor = DecisionTreeRegressor(random_state=0)
regressor.fit(X_train, y_train)

result = regressor.score(X_test, y_test)

print(result)

y_pred = regressor.predict(X_test)
print_err(y_test[y_test > 250000.0]/1000000.0, y_pred[y_test > 250000.0]/1000000.0, 'regresor', 'kula i walec')

x = df_cl.index / 100.0
y_pred = regressor.predict(df_cl_data) / 1000000.0

f1 = plt.figure(1)
f1.suptitle('Predykcja siły chwytu - model drzew decyzyjnych')
plt.plot(x, y_pred, label='Predykcja siły')
plt.plot(x, df_cl_target / 1000000.0, label='Siła rzeczywista')
plt.legend(loc='lower right')
plt.grid()
plt.xlim(0, 60)
plt.title('a)')
plt.xlabel('Czas [s]')
plt.ylabel('Siła [N]')

f2 = plt.figure(2)
f2.suptitle('Predykcja siły chwytu - model drzew decyzyjnych')
y_pred = regressor.predict(df_sp_data) / 1000000.0
plt.plot(x, y_pred, label='Predykcja siły')
plt.plot(x, df_sp_target / 1000000.0, label='Siła rzeczywista')
plt.legend(loc='lower right')
plt.grid()
plt.xlim(0, 60)
plt.title('b)')
plt.xlabel('Czas [s]')
plt.ylabel('Siła [N]')

plt.show()