# Model experimentation library
from datetime import datetime
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction import DictVectorizer
from pysurvival.models.survival_forest import ConditionalSurvivalForestModel, RandomSurvivalForestModel
from pysurvival.utils.metrics import concordance_index
from pysurvival.utils.display import integrated_brier_score
from pysurvival.utils.display import compare_to_actual
from pysurvival.utils import save_model
import mlflow
from mlflow import MlflowClient
import ast
from typing import List
import joblib
from pathlib import Path
import numpy as np

path = Path(__file__).parent / ""


def convertToSArray(data: dict):
    """Convert the time and event arrays to a structured array"""
    y = np.zeros(len(data['E']), dtype={'names': ('E', 'T'),
                                        'formats': ('?', 'i8')})
    y['E'] = data['E'].astype(bool)
    y['T'] = data['T']
    return y


def evalMetrics(model, te_data):
    c_index = concordance_index(model, **te_data)
    ibs = integrated_brier_score(model, figure_size=(15, 5), **te_data)
    results = compare_to_actual(model, is_at_risk=True,  figure_size=(
        16, 6), metrics=['rmse', 'mean', 'median'], **te_data)
    return c_index, ibs, results


def classificationKind(kind: str):
    if kind == "rsf":
        return RandomSurvivalForestModel
    elif kind == "csf":
        return ConditionalSurvivalForestModel
    else:
        raise Exception("Kind Not Supported")


def fetchExperimentID(exp_info, client):
    try:
        # Create experiment
        experiment_id = client.create_experiment(exp_info['exp_name'])
        return experiment_id
    except:
        # Get the experiment id if it already exists
        experiment_id = client.get_experiment_by_name(
            exp_info['exp_name']).experiment_id
        return experiment_id


def getRunBySortMetric(client, experiment_id: str):
    """"
    Searchs the runs in an experiment and returns the run with the highest metric
    """
    rev_run = client.search_runs(
        experiment_id, order_by=["metrics.rmse ASC", "metrics.c_index DESC", "metrics.ibs ASC"])[0]
    return rev_run


def compareRunProd(run, prod_run):
    """"
    Compares a run c_index metric with a prod run's c_index metric and returns the run if its' metric is higher
    """
    if run.data.metrics['c_index'] > prod_run.data.metrics['c_index']:
        return run


def experimentModel(exp_info, tr_data, te_data, param_grid, trees: int, kind: str):
    """"
    Takes in experiment information and a model constructor and logs params and environment variables
    """
    mlflow.set_tracking_uri(exp_info['mlflow_uri'])

    # Initialize client
    client = MlflowClient(exp_info['mlflow_uri'])

    experiment_id = fetchExperimentID(exp_info, client)
    with mlflow.start_run(experiment_id=experiment_id, run_name=exp_info['exp_name']) as run:
        # Get run id
        run_id = run.info.run_uuid

        # Set the notes for the run
        client.set_tag(run_id, exp_info['exp_desc1'], exp_info['exp_desc2'])

        # mlflow.autolog()
        # Define and set custom tag
        tags = exp_info['tags']
        mlflow.set_tags(tags)
        mlflow.set_tag("classification_kind", kind)
        mlflow.set_tag("model_name", exp_info['model_name'])

        # mlflow.set_tag("target_names", ' '.join(target_names))

        # Log python environment details
        # mlflow.log_artifact('./requirements.txt')

        output_kind = classificationKind(kind)

        # Transform the dataset
        data_pipe = Pipeline([('dv', DictVectorizer(sparse=False)),
                              ('minmax', MinMaxScaler()),
                              ('std', StandardScaler())])

        _tr_data = tr_data.copy()
        _tr_data['X'] = data_pipe.fit_transform(tr_data['X'])

        # Model Instancing and Training
        clf = output_kind(num_trees=trees)
        clf.fit(**_tr_data, **param_grid)

        _te_data = te_data.copy()
        _te_data['X'] = data_pipe.transform(te_data['X'])
        (c_index, ibs, results) = evalMetrics(clf, _te_data)

        #mlflow.sklearn.log_model(clf, "model")

        # logging params
        # mlflow.log_artifact(f"{path}/../tmp/data_pipe.sav")
        mlflow.log_param("trees", trees)
        mlflow.log_params(param_grid)
        mlflow.log_dict(results, "results.json")

        # logging metrics
        mlflow.log_metrics({'c_index': c_index,
                            'ibs': ibs,
                            'rmse': results['root_mean_squared_error'],
                            'medab': results['median_absolute_error'],
                            'mab': results['mean_absolute_error']
                            })
    return c_index, ibs


def updateProd(exp_info, client, run):
    """
    Transitions a model to Production Version
    """
    # Registering a new version of the model under the registered model name
    model_uri = f"runs:/{run.info.run_id}/{exp_info['model_name']}"
    mv = mlflow.register_model(
        model_uri, exp_info['model_name'], tags=exp_info['tags'])
    client.transition_model_version_stage(name=exp_info['model_name'],
                                          version=mv.version,
                                          stage="Production", archive_existing_versions=True)
    client.update_model_version(name=exp_info['model_name'],
                                version=mv.version, description=f"The model version {mv.version} was transitioned to Production on {datetime.now()}")


def buildModel(exp_info: dict, tr_data: dict, te_data: dict, rev_run):
    """"
    Takes in a Run and relevant experiment information, builds and logs the model
    """
    mlflow.set_tracking_uri(exp_info['mlflow_uri'])

    # Initialize client
    client = MlflowClient(exp_info['mlflow_uri'])
    experiment_id = fetchExperimentID(exp_info, client)

    param_grid = rev_run.to_dictionary()['data']['params']

    kind = rev_run.data.tags['classification_kind']
    output_kind = classificationKind(kind)

    def parse_params(param_grid):
        for key in param_grid.keys():
            try:
                param_grid[key] = ast.literal_eval(param_grid[key])
            except Exception as e:
                param_grid[key] = param_grid[key]
        return param_grid

    param_grid = parse_params(param_grid)

    with mlflow.start_run(experiment_id=experiment_id, run_name=exp_info['exp_name']) as run:
        # Get run id
        run_id = run.info.run_uuid

        # Set the notes for the run
        client.set_tag(run_id, exp_info['exp_desc1'], exp_info['exp_desc2'])

        # mlflow.autolog()
        # Define and set custom tag
        tags = exp_info['tags']
        mlflow.set_tags(tags)
        mlflow.set_tag("classification_kind", kind)
        mlflow.set_tag("model_name", exp_info["model_name"])

        # create transformation pipeline
        data_pipe = data_pipe = Pipeline([('dv', DictVectorizer(sparse=False)),
                                          ('minmax', MinMaxScaler()),
                                          ('std', StandardScaler())])
        _tr_data = tr_data.copy()
        _tr_data['X'] = data_pipe.fit_transform(tr_data['X'])

        # Initialize and fit model
        trees = param_grid.pop('trees')
        clf = output_kind(num_trees=trees)
        clf.fit(**_tr_data, **param_grid)

        _te_data = te_data.copy()
        _te_data['X'] = data_pipe.transform(te_data['X'])
        (c_index, ibs, results) = evalMetrics(clf, _te_data)

        joblib.dump(data_pipe, f"{path}/../tmp/data_pipe.sav")
        save_model(clf, f"{path}/../tmp/model.zip")

        # Log Params, Artifact and Results
        mlflow.log_artifact(f"{path}/../tmp/data_pipe.sav")
        mlflow.log_artifact(f"{path}/../tmp/model.zip")
        mlflow.log_params(param_grid)
        mlflow.log_param("trees", trees)
        mlflow.log_dict(results, "results.json")

        # logging metrics
        mlflow.log_metrics({'c_index': c_index,
                            'ibs': ibs,
                            'rmse': results['root_mean_squared_error'],
                            'medab': results['median_absolute_error'],
                            'mab': results['mean_absolute_error']
                            })

    return clf, run


def modelProduct(exp_info, tr_data, te_data):
    """"
    Consolidates all the efforts of the preceding functions in the following steps:
    1. Gets the latest run with highest metrics
    2. Checks if a prod version exists
    3. If a prod version exists it fetches the associated prod metadata
    4. A comparison of the latest run and prod run metrics is done: If the latest run has higher metrics then 
        it is built and transitioned to Prod replacing the existing one
    5. If no prod version exists then the latest run is built and transitioned to production
    """
    client = MlflowClient(exp_info['mlflow_uri'])
    experiment_id = fetchExperimentID(exp_info, client)

    # search experiment with highest run > prod run
    latest_run = getRunBySortMetric(client, experiment_id)

    try:
        prod_runs = client.get_latest_versions(
            name=exp_info['model_name'], stages=["Production"])
        # fetching the latest prod version
        prod_info = prod_runs[-1]

        stage_run_metadata = client.get_run(run_id=latest_run.info.run_id)
        prod_run_metadata = client.get_run(run_id=prod_info.run_id)

        # compare latest_run  and prod run
        exp_run = compareRunProd(stage_run_metadata, prod_run_metadata)

        if exp_run:
            # Updating the correct name of the model
            exp_info['model_name'] = exp_run.data.tags['model_name']
            clf, built_run = buildModel(exp_info, tr_data, te_data, exp_run)
            updateProd(exp_info, client, built_run)
    except:
        # Updating the correct name of the model
        exp_info['model_name'] = latest_run.data.tags['model_name']
        clf, built_run = buildModel(exp_info, tr_data, te_data, latest_run)
        updateProd(exp_info, client, built_run)

    return clf


def fetchModel(tracking_uri: str, model_name: str):
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient(tracking_uri)
    version_info = client.search_model_versions(f"name='{model_name}'")
    model = mlflow.pyfunc.load_model(
        model_uri=version_info[0].source.replace(model_name, 'model'))
    return model


def downloadModel(tracking_uri: str, model_name: str = None, search_prefix: str = "Finly") -> None:
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient(tracking_uri)
    if model_name:
        version_info = client.search_model_versions(f"name='{model_name}'")
        run_id = version_info[0].run_id

    else:
        version_info = client.search_registered_models(
            filter_string=f"name LIKE '{search_prefix}%'")
        run_id = version_info[0].latest_versions[0].run_id

    mlflow.artifacts.download_artifacts(
        run_id=run_id, dst_path=f"{path}/../modelproduct /")
