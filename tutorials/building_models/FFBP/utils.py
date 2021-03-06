import os
import pickle
import numpy as np
import tensorflow as tf
from collections import OrderedDict


def snap2pickle(logdir, snap, run_index):
    # Deprecated: this function is defined as ModelSaver method in FFBP.constructors
    path = '/'.join([logdir,'snap_{}.pkl'.format(run_index)])
    try:
        with open(path, 'rb') as old_file:
            old_snap = pickle.load(old_file)
        with open(path, 'wb') as old_file:
            old_snap.append(snap)
            pickle.dump(old_snap, old_file)
    except FileNotFoundError:
        with open(path, 'wb') as new_file:
            out = pickle.dump([snap], new_file)


def new_logdir():
    i=0
    logdir = os.getcwd() + '/logdirs/logdir_000'
    while os.path.exists(logdir):
        i+=.001
        logdir = os.getcwd() + '/logdirs/logdir_{}'.format(str(i)[2:5])
    os.makedirs(logdir)
    return logdir


def list_pickles(logdir):
    # return a list of .pkl files and a list of absolute paths to them
    filenames = [filename for filename in os.listdir(logdir) if '.pkl' in filename]
    paths = [os.path.join(logdir, filename) for filename in filenames]
    return filenames, paths


def load_runlog(runlog_path):
    with open(runlog_path, 'rb') as snap_file:
        test_data = pickle.load(snap_file)
    return test_data


def load_test_data(runlog_path):
    with open(runlog_path, 'rb') as snap_file:
        test_data = pickle.load(snap_file)['test_data']
    return test_data


def get_epochs(runlog_path):
    snaps = load_test_data(runlog_path)
    return [snap['enum'] for snap in snaps]


def get_data_by_key(runlog_path, keys):
    if isinstance(keys, str): keys = [keys]
    snaps = load_test_data(runlog_path)
    return_dict = OrderedDict()
    for k in keys:
        return_dict[k] = [snap[k] for snap in snaps]
    return return_dict


def get_pattern_options(runlog_path, tind, input_dtype=int):
    snap = load_test_data(runlog_path)[tind]
    labels, vectors = snap['labels'], snap['input']
    del snap

    pattern_labels, pattern_vectors = [], []

    for label, vector in zip(labels, vectors):
        pattern_labels.append(label.decode('utf-8'))

        vector_string = np.array2string(vector.astype(input_dtype), separator=',', suppress_small=True)
        pattern_vectors.append(vector_string.replace('[','').replace(']',''))

    return ['{} | {}'.format(pl,pv) for pl, pv in zip(pattern_labels, pattern_vectors)]


def get_layer_dims(runlog_path, layer_names):
    layer_names = [layer_names] if not isinstance(layer_names, (list, tuple)) else layer_names
    layer_dims = {}
    snaps = load_test_data(runlog_path)
    for layer_name in layer_names:
        layer_dims[layer_name] = snaps[0][layer_name]['weights'].shape
    return layer_dims


def get_layer_names(runlog_path):
    snap = load_test_data(runlog_path)[0]
    names = []
    for k, v in snap.items():
        if isinstance(v, dict):
            names.append(k)
    return names


def clipped(x):
    # this handles cases when y * tf.log(y') outputs NaN
    return tf.clip_by_value(x, 1e-10, 1.0)


def cross_entropy(target, activation, name='cross_entropy'):
    return -tf.reduce_sum(target * tf.log(clipped(activation)) + (1 - target) * tf.log(clipped(1 - activation)),
                          name=name)
