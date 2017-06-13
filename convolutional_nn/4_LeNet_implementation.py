from tensorflow.examples.tutorials.mnist import input_data
from tensorflow.contrib.layers import flatten
from helpers import get_batches
from sklearn.utils import shuffle
import tensorflow as tf
import numpy as np


def LeNet(_x_):
    mu = 0
    sd = 0.1
    w = {
        'c1': tf.Variable(tf.truncated_normal([5, 5, 1, 6], mean=mu, stddev=sd)),
        'c2': tf.Variable(tf.truncated_normal([5, 5, 6, 16], mean=mu, stddev=sd)),
        'fc1': tf.Variable(tf.truncated_normal([400, 120], mean=mu, stddev=sd)),
        'fc2': tf.Variable(tf.truncated_normal([120, 84], mean=mu, stddev=sd)),
        'out': tf.Variable(tf.truncated_normal([84, 10], mean=mu, stddev=sd)),
    }
    b = {
        'c1': tf.Variable(tf.truncated_normal([6], mean=mu, stddev=sd)),
        'c2': tf.Variable(tf.truncated_normal([16], mean=mu, stddev=sd)),
        'fc1': tf.Variable(tf.truncated_normal([120], mean=mu, stddev=sd)),
        'fc2': tf.Variable(tf.truncated_normal([84], mean=mu, stddev=sd)),
        'out': tf.Variable(tf.truncated_normal([10], mean=mu, stddev=sd))
    }
    st = [1, 1, 1, 1]
    padding = 'VALID'
    k = 2
    pool_st = [1, k, k, 1]
    pool_k = [1, k, k, 1]
    # Layer 1 -- convolution layer:
    conv1 = tf.nn.conv2d(_x_, filter=w['c1'], strides=st, padding=padding)
    conv1 = tf.nn.bias_add(conv1, bias=b['c1'])
    conv1 = tf.nn.relu(conv1)
    conv1 = tf.nn.max_pool(conv1, ksize=pool_k, strides=pool_st, padding=padding)
    # Layer 2 -- convolution layer:
    conv2 = tf.nn.conv2d(conv1, filter=w['c2'], strides=st, padding=padding)
    conv2 = tf.nn.bias_add(conv2, bias=b['c2'])
    conv2 = tf.nn.relu(conv2)
    conv2 = tf.nn.max_pool(conv2, ksize=pool_k, strides=pool_st, padding=padding)
    # Flatten
    fc1 = flatten(conv2)
    # Layer 3 -- fully connected layer:
    fc1 = tf.add(tf.matmul(fc1, w['fc1']), b['fc1'])
    fc1 = tf.nn.relu(fc1)
    # Layer 4 -- full connected layer:
    fc2 = tf.add(tf.matmul(fc1, w['fc2']), b['fc2'])
    fc2 = tf.nn.relu(fc2)
    # Layer 5 -- fully connected layer:
    out = tf.add(tf.matmul(fc2, w['out']), b['out'])
    # parameters in each layer
    n_parameters(conv1, conv2, fc1, fc2, out)
    # return convolutional neural network
    return out


def n_parameters(layer1, layer2, layer3, layer4, layer5):
    # parameter sharing is assumed
    dim = layer1.get_shape()[3]
    layer1_params = dim * (5 * 5 * 1) + dim * 1
    dim = layer2.get_shape()[3]
    layer2_params = dim * (5 * 5 * 6) + dim * 1
    dim = layer3.get_shape()[1]
    layer3_params = dim * 400 + dim * 1
    dim = layer4.get_shape()[1]
    layer4_params = dim * 120 + dim * 1
    dim = layer5.get_shape()[1]
    layer5_params = dim * 84 + dim * 1
    total_params = layer1_params + layer2_params + layer3_params + layer4_params + layer5_params

    print("Layer 1 Params: {}".format(layer1_params))
    print("Layer 2 Params: {}".format(layer2_params))
    print("Layer 3 Params: {}".format(layer3_params))
    print("Layer 4 Params: {}".format(layer4_params))
    print("Layer 5 Params: {}".format(layer5_params))
    print("Total Params:   {}".format(total_params))


def train_network(sess, x_train, y_train, batch_size, optimizer, x, y):
    x_train, y_train = shuffle(x_train, y_train)
    batches = get_batches(batch_size, x_train, y_train)
    for batch_x, batch_y in batches:
        sess.run(optimizer, feed_dict={
            x: batch_x,
            y: batch_y
        })


def validate_network(sess, x_validation, y_validation, accuracy, x, y, e):
    acc = sess.run(accuracy, feed_dict={
        x: x_validation,
        y: y_validation
    })
    print("{}th epoch accuracy: {:2.3f}%".format(e, acc * 100))
    return acc


def test_network(sess, x_test, y_test, accuracy, x, y):
    acc = sess.run(accuracy, feed_dict={
        x: x_test,
        y: y_test
    })
    print("test accuracy: {:2.3f}%".format(acc * 100))
    return acc


def ConvNet_using_LeNet():
    # dataset
    mnist = input_data.read_data_sets('MNIST_data/', reshape=False)
    x_train, y_train = mnist.train.images, mnist.train.labels
    x_validation, y_validation = mnist.validation.images, mnist.validation.labels
    x_test, y_test = mnist.test.images, mnist.test.labels
    # length assertion
    assert (len(x_train) == len(y_train))
    assert (len(x_validation) == len(y_validation))
    assert (len(x_test) == len(y_test))
    # input image shape
    input_shape = x_train[0].shape[0]  # --> 28*28
    # border padding --> transforming from 28*28 to 32*32 which LeNet can process
    padding = int((32 - input_shape) / 2)
    border = ((0, 0), (padding, padding), (padding, padding), (0, 0))
    x_train = np.pad(x_train, border, 'constant')
    x_validation = np.pad(x_validation, border, 'constant')
    x_test = np.pad(x_test, border, 'constant')
    # shuffle
    x_train, y_train = shuffle(x_train, y_train)
    # placeholders
    x = tf.placeholder(tf.float32, [None, 32, 32, 1])  # None allows to later accept any size
    y = tf.placeholder(tf.int32, [None])
    one_hot_y = tf.one_hot(y, 10)
    # network parameters
    epochs = 10
    batch_size = 128
    learn_rate = 0.01
    # network implementation
    logits = LeNet(x)
    cross_entropy = tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=one_hot_y)
    cost = tf.reduce_mean(cross_entropy)  # loss operation
    optimizer = tf.train.AdamOptimizer(learning_rate=learn_rate).minimize(cost)
    correct_prediction = tf.equal(tf.argmax(logits, 1), tf.argmax(one_hot_y, 1))  # compare with ground truth
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    # session
    init = tf.global_variables_initializer()
    with tf.Session() as sess:
        sess.run(init)
        for e in range(epochs):
            train_network(sess, x_train, y_train, batch_size, optimizer, x, y)
            validate_network(sess, x_validation, y_validation, accuracy, x, y, e)
        test_network(sess, x_test, y_test, accuracy, x, y)


ConvNet_using_LeNet()
