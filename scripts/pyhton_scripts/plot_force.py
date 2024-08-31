import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import medfilt
import hysteresis as hys

def forces_from_dataset(df):
    Vc = 3.3
    MCU_res = 1023.0
    FT_res = 1000000.0 # F/T Sensor sends data in micro Newtons
    curr_sens = 0.185 # current sensor sensitivity V/A
    rot_rang = 190.0 # full sensor rotation angle
    freq = 100.0 # frequency of sent data
    R1 = 3420
    R2 = 6960
    k = 0.765 # motor coefficient Nm/A
    phi = (rot_rang - 180.0) / 2 # angle to fix into xz cords
    gmf = 0.025 / (0.06047 * 0.01) # geometry factor rp / c * rs
    gamma = 20.48 # offset in degrees

    # rotation of fingers
    rs1 = rot_rang - df['RotSens1'] * (rot_rang / MCU_res) + phi
    rs2 = rot_rang - df['RotSens2'] * (rot_rang / MCU_res) + phi
    # resistance of Velostat sensors
    ps1 = (R1 * df['PresSens1'] * (Vc / MCU_res)) / (Vc- df['PresSens1'] * (Vc / MCU_res))
    ps2 = (R2 * df['PresSens2'] * (Vc / MCU_res)) / (Vc- df['PresSens2'] * (Vc / MCU_res))
    # motors current
    cs1 = (df['CurrSens1'] * (Vc / MCU_res) - df['CurrSensInit1'] * (Vc / MCU_res)) / curr_sens
    cs2 =-(df['CurrSens2'] * (Vc / MCU_res) - df['CurrSensInit2'] * (Vc / MCU_res)) / curr_sens

    fx = -df['ForceX'] / FT_res # Minus because pushing into sensor is negative to its z axis
    fy = -df['ForceY'] / FT_res
    fz = -df['ForceZ'] / FT_res
    fr = np.sqrt(np.pow(fx, 2) + np.pow(fy, 2) + np.pow(fz, 2))

    x = df.index / freq # time in s

    # motors torque
    T1 = k * cs1.clip(lower=0)
    T2 = k * cs2.clip(lower=0)
    # force from current
    F_c1 = T1 * gmf * np.sin(np.deg2rad(rs1 + gamma))
    F_c2 = T2 * gmf * np.sin(np.deg2rad(rs2 + gamma))
    
    rho_k1 = 1675.32 # piezorezistive factors
    rho_k2 = 1781.08

    # force on Velostat sensor
    F_vel1 = (rho_k1 / ps1) * np.sin(np.deg2rad(rs1 + gamma))
    F_vel2 = (rho_k2 / ps2) * np.sin(np.deg2rad(rs2 + gamma))

    return [x, fz, F_c1, F_c2, F_vel1, F_vel2]

def print_err(x, x_aprox, name, type):
    print(f'{name} - {type}')
    err = abs(x - x_aprox)
    err_rel = abs(err/x) * 100
    print(f'Err bezwzględny max: {max(err)}')
    print(f'Err bezwzględny średni: {sum(err)/len(err)}')
    print(f'Err względny max: {max(err_rel)}%')
    print(f'Err względny średni: {sum(err_rel)/len(err_rel)}%')

def filter_forces(forces: list, window):
    filtered_forces = []
    for force in forces:
        filtered_forces.append(medfilt(force, window))

    return filtered_forces

# put directory to your datasets here
cylinder_dir = 'datasets/two_finger_grasp_cylinder.csv'
sphere_dir =   'datasets/two_finger_grasp_sphere.csv'

df_cylinder = pd.DataFrame(pd.read_csv(cylinder_dir))
df_sphere = pd.DataFrame(pd.read_csv(sphere_dir))

eff = 0.39
x, fz, F_c1, F_c2, F_vel1, F_vel2 = forces_from_dataset(df=df_cylinder)
[fz_f, F_c1_f, F_c2_f, F_vel1_f, F_vel2_f] = filter_forces([fz, F_c1, F_c2, F_vel1, F_vel2], window=5)
F_vmean = (F_vel1_f + F_vel2_f) / 2
F_mean = (F_vel1_f + F_vel2_f + (F_c1_f + F_c2_f) * eff) / 4


treshold = 0.125 * 2

cut_F_vel1 = F_vel1_f[fz > treshold]
cut_F_vel2 = F_vel2_f[fz > treshold]
cut_F_vmean = F_vmean[fz > treshold]
cut_F_c1 = F_c1_f[fz > treshold]
cut_F_c2 = F_c2_f[fz > treshold]
cut_F_mean = F_mean[fz > treshold]

print_err(fz_f[fz_f > treshold], cut_F_vel1, 'Velostat 1', 'cylinder')
print_err(fz_f[fz_f > treshold], cut_F_vel2, 'Velostat 2', 'cylinder')
print_err(fz_f[fz_f > treshold], cut_F_vmean, 'Velostat średnia', 'cylinder')
print_err(fz_f[fz_f > treshold], cut_F_c1 * eff, 'Prąd 1', 'cylinder')
print_err(fz_f[fz_f > treshold], cut_F_c2 * eff, 'Prąd 2', 'cylinder')
print_err(fz_f[fz_f > treshold], cut_F_mean, 'Średnia', 'cylinder')

f1 = plt.figure(1)
f1.suptitle('Estymacja siły chwytu - czujnik siły')
plt.plot(x, F_vel1_f, label = 'Siła chwytu 1')
plt.plot(x, F_vel2_f, label = 'Siła chwytu 2')
plt.plot(x, F_vmean, label = 'Siła średnia')
plt.plot(x, fz_f, label = 'Siła rzeczywista')
plt.legend(loc='lower right')
plt.grid()
plt.xlim(0, 105)
plt.title('a)')
plt.xlabel('Czas [s]')
plt.ylabel('Siła [N]')

f2 = plt.figure(2)
f2.suptitle('Estymacja siły chwytu - czujnik prądu')
plt.plot(x, F_c1_f, label = 'Siła chwytu 1')
plt.plot(x, F_c2_f, label = 'Siła chwytu 2')
plt.plot(x, fz_f, label = 'Siła rzeczywista')
plt.legend(loc='lower right')
plt.grid()
plt.xlim(0, 105)
# plt.title('a)')
plt.xlabel('Czas [s]')
plt.ylabel('Siła [N]')

f3 = plt.figure(3)
f3.suptitle('Estymacja siły chwytu - czujnik prądu')
plt.plot(x, F_c1_f * eff, label = 'Siła chwytu 1')
plt.plot(x, F_c2_f * eff, label = 'Siła chwytu 2')
plt.plot(x, fz_f, label = 'Siła rzeczywista')
plt.legend(loc='lower right')
plt.grid()
plt.xlim(0, 105)
plt.title('a)')
plt.xlabel('Czas [s]')
plt.ylabel('Siła [N]')

f4 = plt.figure(4)
plt.suptitle('Estymacja siły chwytu - średnia arytmetyczna')
plt.plot(x, F_mean, label = 'Średnia wszystkich sił')
plt.plot(x, fz, label = 'Siła rzeczywista')
plt.legend(loc='lower right')
plt.grid()
plt.xlim(0, 105)
plt.title('a)')
plt.xlabel('Czas [s]')
plt.ylabel('Siła [N]')


x, fz, F_c1, F_c2, F_vel1, F_vel2 = forces_from_dataset(df=df_sphere)
[fz_f, F_c1_f, F_c2_f, F_vel1_f, F_vel2_f] = filter_forces([fz, F_c1, F_c2, F_vel1, F_vel2], window=5)
F_vmean = (F_vel1_f + F_vel2_f) / 2
F_mean = (F_vel1_f + F_vel2_f + (F_c1_f + F_c2_f) * eff) / 4


treshold = 0.125 * 2

cut_F_vel1 = F_vel1_f[fz > treshold]
cut_F_vel2 = F_vel2_f[fz > treshold]
cut_F_vmean = F_vmean[fz > treshold]
cut_F_c1 = F_c1_f[fz > treshold]
cut_F_c2 = F_c2_f[fz > treshold]
cut_F_mean = F_mean[fz > treshold]

print_err(fz_f[fz_f > treshold], cut_F_vel1, 'Velostat 1', 'kula')
print_err(fz_f[fz_f > treshold], cut_F_vel2, 'Velostat 2', 'kula')
print_err(fz_f[fz_f > treshold], cut_F_vmean, 'Velostat średnia', 'kula')
print_err(fz_f[fz_f > treshold], cut_F_c1 * eff, 'Prąd 1', 'kula')
print_err(fz_f[fz_f > treshold], cut_F_c2 * eff, 'Prąd 2', 'kula')
print_err(fz_f[fz_f > treshold], cut_F_mean, 'Średnia', 'kula')

f5 = plt.figure(5)
f5.suptitle('Estymacja siły chwytu - czujnik siły')
plt.plot(x, F_vel1_f, label = 'Siła chwytu 1')
plt.plot(x, F_vel2_f, label = 'Siła chwytu 2')
plt.plot(x, F_vmean, label = 'Średnia siła')
plt.plot(x, fz_f, label = 'Siła rzeczywista')
plt.legend(loc='lower right')
plt.grid()
plt.xlim(0, 105)
plt.title('b)')
plt.xlabel('Czas [s]')
plt.ylabel('Siła [N]')

f6 = plt.figure(6)
f6.suptitle('Estymacja siły chwytu - czujnik prądu')
plt.plot(x, F_c1_f, label = 'Siła chwytu 1')
plt.plot(x, F_c2_f, label = 'Siła chwytu 2')
plt.plot(x, fz_f, label = 'Siła rzeczywista')
plt.legend(loc='upper right')
plt.grid()
plt.xlim(0, 90)
plt.title('b)')
plt.xlabel('Czas [s]')
plt.ylabel('Siła [N]')

f7 = plt.figure(7)
f7.suptitle('Estymacja siły chwytu - czujnik prądu')
plt.plot(x, F_c1_f * eff, label = 'Siła chwytu 1')
plt.plot(x, F_c2_f * eff, label = 'Siła chwytu 2')
plt.plot(x, fz_f, label = 'Siła rzeczywista')
plt.legend(loc='lower right')
plt.grid()
plt.xlim(0, 105)
plt.title('b)')
plt.xlabel('Czas [s]')
plt.ylabel('Siła [N]')

f8 = plt.figure(8)
f8.suptitle('Estymacja siły chwytu - czujnik prądu')
plt.plot(x, F_mean, label = 'Średnia wszystkich sił')
plt.plot(x, fz_f, label = 'Siła rzeczywista')
plt.legend(loc='lower right')
plt.grid()
plt.xlim(0, 105)
plt.title('b)')
plt.xlabel('Czas [s]')
plt.ylabel('Siła [N]')


plt.show()
