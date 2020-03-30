# profiling utilities
import psutil
import shutil

p = psutil.Process()

# imports
import numpy as np
import os
import json
import pandas as pd
import time
import subprocess
import pickle

# data processing
typeList = [
    'outlyingScatterPlot',
    'skewedScatterPlot',
    'clumpyScatterPlot',
    'sparsedScatterPlot',
    'striatedScatterPlot',
    'convexScatterPlot',
    'skinnyScatterPlot',
    'stringyScatterPlot',
    'monotonicScatterPlot']

with open('../data/ScagnosticsTypicalData2.json') as f:
    typicalData2 = json.load(f)

with open('../data/RealWorldData10.json') as f:
    realWorldData10 = json.load(f)

numPoints = 0  # minimum number of bins
X_real10 = []
y_real10 = []
for ds in realWorldData10:
    for d in ds:
        if not ((np.array(d['scagnostics']) > 1).any() or (np.array(d['scagnostics']) < 0).any()) and np.sum(
                d['rectangularBins']) >= numPoints:
            X_real10.append(d['rectangularBins'])
            y_real10.append(d['scagnostics'])

X_typical2 = []
y_typical2 = []
y_typical_label2 = []
for ds in typicalData2:
    for d in ds:
        # filter out invalid data
        if not ((np.array(d['scagnostics']) > 1).any() or (np.array(d['scagnostics']) < 0).any()) and np.sum(
                d['rectangularBins']) >= numPoints:
            X_typical2.append(d['rectangularBins'])
            y_typical2.append(d['scagnostics'])
            y_typical_label2.append([1 if tl == d['dataSource'] else 0 for tl in typeList])

X_real10 = np.array(X_real10)
y_real10 = np.array(y_real10)

X_typical2 = np.array(X_typical2)
y_typical2 = np.array(y_typical2)

X = np.concatenate([X_real10, X_typical2])
y = np.concatenate([y_real10, y_typical2])
# Re-shape the data
X = X.reshape(X.shape[0], X.shape[1], X.shape[2], 1)
# # training part
# from keras.models import Sequential
# from keras.layers import Dense
# from keras.layers import Flatten
# from keras.layers import Conv2D
# from keras.layers import MaxPooling2D
# from keras.layers import Dropout
# from keras.utils import plot_model
# from keras.regularizers import l2
# from keras.optimizers import SGD
# from keras.layers import BatchNormalization

# # learned several reasons from here: https://machinelearningmastery.com/how-to-develop-a-cnn-from-scratch-for-cifar-10-photo-classification/
# def create_cnn_model():
#     model = Sequential()
#     model.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform', padding='same', input_shape=(40, 40, 1)))
#     model.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform', padding='same'))
#     model.add(MaxPooling2D((2, 2)))
#     model.add(Dropout(0.1))
#     model.add(Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_uniform', padding='same'))
#     model.add(Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_uniform', padding='same'))
#     model.add(MaxPooling2D((2, 2)))
#     model.add(Dropout(0.1))
#     model.add(Flatten())
#     model.add(Dense(128, activation='relu', kernel_initializer='he_uniform'))
#     model.add(Dropout(0.1))
#     opt = SGD(lr=0.001, momentum=0.9)
#     model.add(Dense(9, activation='relu'))
#     # compile model
#     model.compile(optimizer=opt, loss='mse')
#     return model

# model = create_cnn_model()

# from keras.callbacks import EarlyStopping
# from keras.callbacks import ModelCheckpoint
# mc = ModelCheckpoint('best_model.h5', monitor='val_loss', mode='min', save_best_only=True)
# es = EarlyStopping(monitor='val_loss', mode='min', patience=50)

# model.fit(X, y, validation_split=0.33, epochs=500, callbacks=[mc, es])

# load model
import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
from keras.models import load_model

model = load_model('best_model.h5')

# Setting data
num_runs = 31
all_rows = num_runs + 1
# cpu_percent
cpu_percent = np.zeros(all_rows)
# cpu_times
cpu_times_user = np.zeros(all_rows)
cpu_times_system = np.zeros(all_rows)
cpu_times_children_user = np.zeros(all_rows)
cpu_times_children_system = np.zeros(all_rows)
# memory_percent
memory_percent = np.zeros(all_rows)
# disk_usage
disk_usage_total = np.zeros(all_rows)
disk_usage_used = np.zeros(all_rows)
disk_usage_free = np.zeros(all_rows)
# # io_counters
# io_counters_readbytes = np.zeros(all_rows)
# io_counters_writebytes = np.zeros(all_rows)
# memory_full_info
memory_full_info_rss = np.zeros(all_rows)
memory_full_info_vms = np.zeros(all_rows)
memory_full_info_pfaults = np.zeros(all_rows)
memory_full_info_pageins = np.zeros(all_rows)
memory_full_info_uss = np.zeros(all_rows)
time_period = np.zeros(all_rows)


def set_data(p, i, period):
    # cpu_percent
    cpu_percent[i] = p.cpu_percent()
    # cpu_time
    cpu_times = p.cpu_times()
    cpu_times_user[i] = cpu_times.user
    cpu_times_system[i] = cpu_times.system
    cpu_times_children_user[i] = cpu_times.children_user
    cpu_times_children_system[i] = cpu_times.children_system
    # memory_percent
    memory_percent[i] = p.memory_percent()
    # disk_usage
    disk_usage = shutil.disk_usage('./')
    disk_usage_total[i] = disk_usage.total
    disk_usage_used[i] = disk_usage.used
    disk_usage_free[i] = disk_usage.free
    #     # io_counters only available on Linux or Windows
    #     io_counters = p.io_counters()
    #     io_counters_read_bytes[i] = io_counters.read_bytes
    #     io_counters_write_bytes[i] = io_counters.write_bytes
    # memory_full_info
    memory_full_info = p.memory_full_info()
    memory_full_info_rss[i] = memory_full_info.rss
    memory_full_info_vms[i] = memory_full_info.vms
    memory_full_info_pfaults[i] = memory_full_info.pfaults
    memory_full_info_pageins[i] = memory_full_info.pageins
    memory_full_info_uss[i] = memory_full_info.uss
    time_period[i] = period


# start a subprocess to monitor fs_usage
# pro = subprocess.Popen([f'fs_usage {p.pid}'], shell=True, stdout=subprocess.PIPE, preexec_fn=os.setsid)

# run for several times
start = time.perf_counter_ns()
for run_idx in range(num_runs):
    y_hat = model.predict(X)
    period = time.perf_counter_ns() - start
    set_data(p, run_idx, period)

# add last one out of the loop
all = time.perf_counter_ns() - start
# terminate the fs_usage monitoring
# pro.terminate()

set_data(p, num_runs, all)

print(f'Total time {all}')

# make data frame
df = pd.DataFrame()
# cpu_percent
df['cpu_percent'] = cpu_percent
# cpu_times
df['cpu_times_user'] = cpu_times_user
df['cpu_times_system'] = cpu_times_system
df['cpu_times_children_user'] = cpu_times_children_user
df['cpu_times_children_system'] = cpu_times_children_system
# memory_percent
df['memory_percent'] = memory_percent
# disk_usage
df['disk_usage_total'] = disk_usage_total
df['disk_usage_used'] = disk_usage_used
df['disk_usage_free'] = disk_usage_free
# # io_counters
# df['io_counters_read_bytes'] = io_counters_read_bytes
# df['io_counters_write_bytes'] = io_counters_write_bytes
# memory_full_info
df['memory_full_info_rss'] = memory_full_info_rss
df['memory_full_info_vms'] = memory_full_info_vms
df['memory_full_info_pfaults'] = memory_full_info_pfaults
df['memory_full_info_pageins'] = memory_full_info_pageins
df['memory_full_info_uss'] = memory_full_info_uss
df['time_period'] = time_period
# save file
import calendar

ts = str(calendar.timegm(time.gmtime()))
df.to_csv(f'cnn-{ts}.csv')
# with open(f'cnn-fs_usage-{ts}.txt', 'w') as f:
#     for l in pro.stdout.readlines():
#         f.write('%s\n' % l)
