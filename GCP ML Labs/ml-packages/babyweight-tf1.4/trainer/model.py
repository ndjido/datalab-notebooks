#!/usr/bin/env python

# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import tensorflow as tf

import featurizer
import task
import metadata

# ************************************************************************************
# YOU MAY MODIFY THESE FUNCTIONS TO USE DIFFERENT ESTIMATORS OR CONFIGURE THE CURRENT ONES
# ************************************************************************************


def create_classifier(config, hyper_params):
    """ Create a DNNLinearCombinedClassifier based on the hyper_params

    Args:
        config: used for model directory
        hyper_params: dictionary of hyper-parameters
    Returns:
        DNNLinearCombinedClassifier
    """

    feature_columns = list(featurizer.create_feature_columns().values())

    deep_columns, wide_columns = featurizer.get_deep_and_wide_columns(
        feature_columns
    )

    linear_optimizer = tf.train.FtrlOptimizer(learning_rate=hyper_params.learning_rate)
    dnn_optimizer = tf.train.AdagradOptimizer(learning_rate=hyper_params.learning_rate)

    classifier = tf.estimator.DNNLinearCombinedClassifier(

        n_classes=len(metadata.TARGET_LABELS),
        label_vocabulary=metadata.TARGET_LABELS,

        linear_optimizer=linear_optimizer,
        linear_feature_columns=wide_columns,

        dnn_feature_columns=deep_columns,
        dnn_optimizer=dnn_optimizer,

        weight_column=metadata.WEIGHT_COLUMN_NAME,

        dnn_hidden_units=construct_hidden_units(hyper_params),
        dnn_activation_fn=tf.nn.relu,
        dnn_dropout=hyper_params.dropout_prob,

        config=config,
    )

    print("creating a classification model: {}".format(classifier))

    return classifier


def create_regressor(config, hyper_params):
    """ Create a DNNLinearCombinedRegressor based on the hyper_params object

    Args:
        config: used for model directory
        hyper_params: dictionary of hyper-parameters
    Returns:
        DNNLinearCombinedRegressor
    """

    feature_columns = list(featurizer.create_feature_columns().values())

    deep_columns, wide_columns = featurizer.get_deep_and_wide_columns(
        feature_columns
    )

    linear_optimizer = tf.train.FtrlOptimizer(learning_rate=hyper_params.learning_rate)
    dnn_optimizer = tf.train.AdagradOptimizer(learning_rate=hyper_params.learning_rate)

    regressor = tf.estimator.DNNLinearCombinedRegressor(

        linear_optimizer=linear_optimizer,
        linear_feature_columns=wide_columns,

        dnn_feature_columns=deep_columns,
        dnn_optimizer=dnn_optimizer,

        weight_column=metadata.WEIGHT_COLUMN_NAME,

        dnn_hidden_units=construct_hidden_units(hyper_params),
        dnn_activation_fn=tf.nn.relu,
        dnn_dropout=hyper_params.dropout_prob,

        config=config,
    )

    print("creating a regression model: {}".format(regressor))

    return regressor

# ************************************************************************************
# YOU NEED TO MODIFY THIS FUNCTIONS IF YOU WANT TO IMPLEMENT A CUSTOM ESTIMATOR
# ************************************************************************************


def create_estimator(config, hyper_params):
    """ Create a custom estimator based on _model_fn

    Args:
        config - used for model directory
    Returns:
        Estimator
    """

    def _model_fn(features, labels, mode):
        """ model function for the custom estimator"""

        # Create input layer based on features
        # input_layer = None

        # Create hidden layers (dense, fully_connected, cnn, rnn, dropouts, etc.) given the input layer
        # hidden_layers = None

        # Create output layer given the hidden layers
        # output_layer = None

        # Specify the model output (i.e. predictions) given the output layer
        predictions = None

        # Specify the export output based on the predictions
        export_outputs = {
            'predictions': tf.estimator.export.PredictOutput(predictions)
        }

        # Calculate loss based on output and labels
        loss = None

        # Create Optimiser
        optimizer = tf.train.AdamOptimizer(
            learning_rate=hyper_params.learning_rate)

        # Create training operation
        train_op = optimizer.minimize(
            loss=loss, global_step=tf.train.get_global_step())

        # Specify additional evaluation metrics
        eval_metric_ops = None

        # Provide an estimator spec
        estimator_spec = tf.estimator.EstimatorSpec(mode=mode,
                                                    loss=loss,
                                                    train_op=train_op,
                                                    eval_metric_ops=eval_metric_ops,
                                                    predictions=predictions,
                                                    export_outputs=export_outputs
                                                    )
        return estimator_spec

    print("creating a custom estimator")

    return tf.estimator.Estimator(model_fn=_model_fn,
                                  config=config)


# ************************************************************************************
# THIS IS A HELPER FUNCTION TO CREATE GET THE HIDDEN LAYER UNITS
# ************************************************************************************


def construct_hidden_units(hyper_params):
    """ Create the number of hidden units in each layer

    if the hyper_params.layer_sizes_scale_factor > 0 then it will use a "decay" mechanism
    to define the number of units in each layer. Otherwise, hyper_params.hidden_units
    will be used as-is.

    Returns:
        list of int
    """
    hidden_units = list(map(int, hyper_params.hidden_units.split(',')))

    if hyper_params.layer_sizes_scale_factor > 0:
        first_layer_size = hidden_units[0]
        scale_factor = hyper_params.layer_sizes_scale_factor
        num_layers = hyper_params.num_layers

        hidden_units = [
            max(2, int(first_layer_size * scale_factor ** i))
            for i in range(num_layers)
        ]

    print("Hidden units structure: {}".format(hidden_units))

    return hidden_units
