"""
The ``mlflow.pysurv`` module provides an API for logging and loading PySurvival models. This module
exports PySurvival models with the following flavors:
Pysurv (native) format
    This is the main flavor that can be loaded back into PySurv.
:py:mod:`mlflow.pyfunc`
    Produced for use by generic pyfunc-based deployment tools and batch inference.
"""

from __future__ import absolute_import

import os

import mlflow.tracking
import pysurvival
import scripts
import yaml
from mlflow import pyfunc
from mlflow.models import Model
from mlflow.utils.environment import _mlflow_conda_env
from mlflow.utils.model_utils import _get_flavor_configuration

FLAVOR_NAME = "pysurvival"

DEFAULT_CONDA_ENV = _mlflow_conda_env(
    additional_conda_deps=[
        "pysurvival={}".format(pysurvival.__version__),
    ],
    additional_pip_deps=None,
    additional_conda_channels=None,
)


def save_model(pysurvival_model, path, conda_env=None, mlflow_model=Model()):
    """
    Save a PySurvival model to a path on the local file system.
    :param pysurvival_model: PySurvival model to be saved.
    :param path: Local path where the model is to be saved.
    :param conda_env: Either a dictionary representation of a Conda environment or the path to a
                      Conda environment yaml file. If provided, this decribes the environment
                      this model should be run in. At minimum, it should specify the dependencies
                      contained in ``mlflow.pysurvival.DEFAULT_CONDA_ENV``. If `None`, the default
                      ``mlflow.pysurvival.DEFAULT_CONDA_ENV`` environment will be added to the model.
                      The following is an *example* dictionary representation of a Conda
                      environment::
                        {
                            'name': 'mlflow-env',
                            'channels': ['defaults'],
                            'dependencies': [
                                'python=3.7.0',
                                'pysurvival=0.1.2',
                            ]
                        }
    :param mlflow_model: MLflow model config this flavor is being added to.
    >>> import mlflow
    >>> # Build, compile, and train your model
    >>> pysurvival_model = ...
    >>> pysurvival_model_path = ...
    >>> pysurvival_model.fit(X, T, E, max_features = 'sqrt', max_depth = 5, min_node_size = 10, alpha = 0.05, minprop= 0.1, num_threads = -1, weights = None, sample_size_pct = 0.63, importance_mode = 'normalized_permutation', seed = None, save_memory=False )
    ... # Save the model as an MLflow Model
    >>> mlflow.pysurvival.save_model(pysurvival_model, pysurvival_model_path)
    """
    if os.path.exists(path):
        raise Exception("Path '{}' already exists".format(path))
    os.makedirs(path)
    model_data_subpath = "model.zip"
    pysurvival.utils.save_model(
        pysurvival_model, os.path.join(path, model_data_subpath))

    conda_env_subpath = "conda.yaml"
    if conda_env is None:
        conda_env = DEFAULT_CONDA_ENV
    elif not isinstance(conda_env, dict):
        with open(conda_env, "r") as f:
            conda_env = yaml.safe_load(f)
    with open(os.path.join(path, conda_env_subpath), "w") as f:
        yaml.safe_dump(conda_env, stream=f, default_flow_style=False)

    pyfunc.add_to_model(mlflow_model, loader_module="scripts.pysurv",
                        data=model_data_subpath, env=conda_env_subpath)
    mlflow_model.add_flavor(
        FLAVOR_NAME, pysurvival_version=pysurvival.__version__, data=model_data_subpath)
    mlflow_model.save(os.path.join(path, "MLmodel"))


def log_model(pysurvival_model, artifact_path, conda_env=None, **kwargs):
    """
    Log a PySurvival model as an MLflow artifact for the current run.
    :param pysurvival_model: PySurival model to be saved.
    :param artifact_path: Run-relative artifact path.
    :param conda_env: Either a dictionary representation of a Conda environment or the path to a
                      Conda environment yaml file. If provided, this decribes the environment
                      this model should be run in. At minimum, it should specify the dependencies
                      contained in ``mlflow.pysurvival.DEFAULT_CONDA_ENV``. If `None`, the default
                      ``mlflow.pysurvival.DEFAULT_CONDA_ENV`` environment will be added to the model.
                      The following is an *example* dictionary representation of a Conda
                      environment::
                        {
                            'name': 'mlflow-env',
                            'channels': ['defaults'],
                            'dependencies': [
                                'python=3.7.0',
                                'pysurvival=0.1.2',
                            ]
                        }
    :param kwargs: kwargs to pass to ``pysurvival.save`` method.
    >>> from pysurvival import Dense, layers
    >>> import mlflow
    >>> # Build, compile, and train your model
    >>> pysurvival_model = ...
    >>> pysurvival_model.fit(X, T, E, max_features = 'sqrt', max_depth = 5, min_node_size = 10, alpha = 0.05, minprop= 0.1, num_threads = -1, weights = None, sample_size_pct = 0.63, importance_mode = 'normalized_permutation', seed = None, save_memory=False )
    >>> # Log metrics and log the model
    >>> with mlflow.start_run() as run:
    >>>   mlflow.pysurvival.log_model(pysurvival_model, "models")
    """
    Model.log(artifact_path=artifact_path, flavor=scripts.pysurv,
              pysurvival_model=pysurvival_model, conda_env=conda_env, **kwargs)


def _load_model(model_file):
    return pysurvival.utils.load_model(model_file)


class _PySurvivalModelWrapper:
    def __init__(self, pysurvival_model):
        self.pysurvival_model = pysurvival_model

    def predict(self, X, t=None):
        hazard = self.pysurvival_model.predict_hazard(X, t)
        survival = self.pysurvival_model.survival(X, t)
        risk = self.pysurvival_model.survival(X)
        return [hazard, survival, risk]


def _load_pyfunc(model_file):
    """
    Load PyFunc implementation. Called by ``pyfunc.load_pyfunc``.
    """
    m = _load_model(model_file)
    return _PySurvivalModelWrapper(m)


def load_model(path, run_id=None):
    """
    Load a PySurvival model from a local file (if ``run_id`` is None) or a run.
    :param path: Local filesystem path or run-relative artifact path to the model saved
                 by :py:func:`mlflow.pysurvival.log_model`.
    :param run_id: Run ID. If provided, combined with ``path`` to identify the model.
    >>> # Load persisted model as a PySurvival model or as a PyFunc, call predict() on a Pandas DataFrame
    >>> pysurvival_model = mlflow.pysurvival.load_model("models", run_id="96771d893a5e46159d9f3b49bf9013e2")
    >>> predictions = pysurvival_model.predict(x_test)
    """
    if run_id is not None:
        path = mlflow.tracking.utils._get_model_log_dir(
            model_name=path, run_id=run_id)
    path = os.path.abspath(path)
    flavor_conf = _get_flavor_configuration(
        model_path=path, flavor_name=FLAVOR_NAME)
    # Flavor configurations for models saved in MLflow version <= 0.8.0 may not contain a
    # `data` key; in this case, we assume the model artifact path to be `model.h5`
    pysurvival_model_artifacts_path = os.path.join(
        path, flavor_conf.get("data", "model.zip"))
    return _load_model(model_file=pysurvival_model_artifacts_path)
