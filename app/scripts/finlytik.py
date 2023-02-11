from asyncio import run
from datetime import datetime
import warnings
import random
import os

import numpy as np
import pandas as pd
import joblib

from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split


from pysurvival.utils.metrics import concordance_index
from pysurvival.utils.display import integrated_brier_score
from pysurvival.models.survival_forest import ConditionalSurvivalForestModel
from pysurvival.utils.display import compare_to_actual
from pysurvival.utils import save_model, load_model

from prefect import flow, task

from typing import Dict

# Model experimentation library
import mlflow
from mlflow import MlflowClient

# Hyperparameter tunning library
import optuna

# Plotting library
import matplotlib.pyplot as plt
# Prevent figures from displaying by turning interactive mode off using the function
plt.ioff()
warnings.filterwarnings("ignore")
os.environ["AWS_PROFILE"] = "bebeto"

# Set seed
SEED = 42


def set_seeds(seed=SEED):
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)
    # tf.random.set_seed(seed)
    np.random.seed(seed)


def set_global_determinism(seed=SEED):
    set_seeds(seed=seed)

    os.environ['TF_DETERMINISTIC_OPS'] = '1'
    os.environ['TF_CUDNN_DETERMINISTIC'] = '1'


set_global_determinism(seed=SEED)

################################
##### Experiment Constants #####
################################
exp_info = {'exp_name': 'Finlytik T',
            'model_name': 'finsurv',
            'study_name': 'Finlytik-PySurvival T',
            'mlflow_uri': "postgresql://postgres:postgres123@172.22.0.1:5432/mlflow",
            'optuna_uri': "postgresql://postgres:postgres123@172.22.0.1:5432/optuna",
            'artifact_repo': '../mlflow_repo',
            'exp_desc1': 'mlflow.note.content',
            'exp_desc2': 'Experiment for hyperparameter optimzation for C. Survival for Credit Risk',
            'tags': {"Application": "Finlytik - Credit Risk App",
                     "release.version": "0.1.0"}
            }


#########################
##### Fetching Data #####
#########################
@task(name="clean_data")
def clean_data(df: pd.DataFrame):
    def emp_prep(val):
        if pd.isnull(val):
            return 0

        emp = str(val).replace('\+ years', '')
        emp = emp.replace('< 1 year', '0')
        emp = emp.replace(' years', '')
        emp = emp.replace(' year', '')
        emp = emp.replace('+', '')
        return float(emp)

    df.columns = list(map(lambda x: x.lower().replace(" ", "_"), df.columns))
    df.dropna(axis=0, inplace=True)
    df = df.drop(columns=['loan_id', 'customer_id'])
    df = df.drop_duplicates()
    df['loan_status'] = np.where(
        df.loc[:, 'loan_status'].isin(['Charged Off']), 0, 1)
    df['years_in_current_job'] = df['years_in_current_job'].apply(emp_prep)

    categorical = list(df.select_dtypes(include=['object']).columns)
    df[categorical] = df[categorical].astype(str)

    return df


#########################
##### Fetching Data #####
#########################
@task(name="fetch_data")
def fetch_data(filename: str = "./loan_data.csv"):
    df = pd.read_csv(filename)
    return df

##########################
##### Preprocessing ######
##########################


@task(name="preprocessing")
def preprocessing(df: pd.DataFrame, N: int = 5000):
    # Sample data in 50:50 ratio of the loan_status
    df = df.groupby('loan_status').apply(
        lambda x: x.sample(n=N)).reset_index(drop=True)

    # Splitting the data into train and test sets
    train, test = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df['loan_status'])

    tr_data = {'X': train.drop(['months_since_last_delinquent', 'loan_status'], axis=1),
               'T': train['months_since_last_delinquent'].values.ravel(),
               'E': train['loan_status'].values.ravel()}

    te_data = {'X': test.drop(['months_since_last_delinquent', 'loan_status'], axis=1),
               'T': test['months_since_last_delinquent'].values.ravel(),
               'E': test['loan_status'].values.ravel()}

    # Transforming Vectorizing the categorical Ffeatures
    trnsfm_pipe = Pipeline([('dv', DictVectorizer(sparse=False)),
                            ('minmax', MinMaxScaler()),
                            ('std', StandardScaler())])
    tr_data['X'] = trnsfm_pipe.fit_transform(
        tr_data['X'].to_dict(orient='records'))
    te_data['X'] = trnsfm_pipe.transform(
        te_data['X'].to_dict(orient='records'))

    return tr_data, te_data, trnsfm_pipe


###############################
##### Experiment Logging ######
###############################
@task(name="experiment_logging")
def experiment_logging(exp_info, model_cons, tr_data, te_data, param_grid, trees, t_pipe):
    mlflow.set_tracking_uri(exp_info['mlflow_uri'])

    # Initialize client
    client = MlflowClient()

    try:
        # Create experiment
        experiment_id = client.create_experiment(
            exp_info['exp_name'], artifact_location=exp_info['artifact_repo'])
    except:
        # Get the experiment id if it already exists
        experiment_id = client.get_experiment_by_name(
            exp_info['exp_name']).experiment_id

    def eval_metrics(model, te_data):
        c_index = concordance_index(model, **te_data)
        ibs = integrated_brier_score(model, figure_size=(15, 5), **te_data)
        results = compare_to_actual(model, is_at_risk=True,  figure_size=(
            16, 6), metrics=['rmse', 'mean', 'median'], **te_data)

        return c_index, ibs, results

    with mlflow.start_run(experiment_id=experiment_id, run_name=exp_info['exp_name']) as run:
        # Get run id
        run_id = run.info.run_uuid

        # Set the notes for the run
        client.set_tag(run_id, exp_info['exp_desc1'], exp_info['exp_desc2'])

        # Define and set custom tag
        tags = exp_info['tags']
        mlflow.set_tags(tags)

        # Log python environment details
        mlflow.log_artifact('./requirements.txt')

        # Model Instancing and Training
        model = model_cons(trees)
        model.fit(**tr_data, **param_grid)

        (c_index, ibs, results) = eval_metrics(model, te_data)

        # logging params
        mlflow.log_params(param_grid)

        # logging metrics
        mlflow.log_metrics({'c_index': c_index,
                            'ibs': ibs, 'rmse': results['root_mean_squared_error'],
                                        'medab': results['median_absolute_error'],
                                        'mab': results['mean_absolute_error']
                            })
        # Logging the preprocessor
        dv_path = "../staging/dv.joblib"
        joblib.dump(t_pipe, dv_path)
        mlflow.log_artifact(dv_path, artifact_path="preprocessor")

        # Logging the model artifact
        model_path = "../staging/model.zip"
        save_model(model, model_path)
        mlflow.log_artifact(model_path, artifact_path="model")

    # Registering a new version of the model under the registered model name
    model_uri = f"runs:/{run.info.run_id}/{exp_info['model_name']}"
    mv = mlflow.register_model(
        model_uri, exp_info['model_name'], tags=exp_info['tags'])
    client.transition_model_version_stage(name=exp_info['model_name'],
                                          version=mv.version,
                                          stage="Staging")
    client.update_model_version(name=exp_info['model_name'],
                                version=mv.version,
                                description=f"The model version {mv.version} was transitioned to Staging on {datetime.now()}")
    return c_index, ibs

#########################
######### Main ##########
#########################


@flow
def model_search(exp_info: Dict = exp_info, num_trials: int = 2):
    def objective(trial):
        df = fetch_data()
        df = clean_data(df)
        tr_data, te_data, dv = preprocessing(df)
        trees = trial.suggest_int("num_trees", 100, 150)
        param_grid = {
            "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2", "all"]),
            "min_node_size": trial.suggest_int("min_node_size", 15, 25),
            "alpha": trial.suggest_float("alpha", 0.04, 0.06),
            "minprop": trial.suggest_float("minprop", 0.05, 0.15),
            "max_depth": trial.suggest_int("max_depth", 4, 12),
            "seed": 42,
        }

        c_index, ibs = experiment_logging(
            exp_info, ConditionalSurvivalForestModel, tr_data, te_data, param_grid, trees, dv)
        return c_index, ibs

    study = optuna.create_study(directions=[
        "maximize", "minimize"], study_name=exp_info['study_name'], load_if_exists=True, storage=exp_info['optuna_uri'])  #
    study.optimize(objective, n_trials=num_trials, show_progress_bar=True)


#########################
#### Productionizing ####
#########################
@task(name="model_product")
def model_product():
    client = MlflowClient(tracking_uri=exp_info['mlflow_uri'])

    # search for the latest staging version
    latest_stage_info = client.get_latest_versions(
        name=exp_info['model_name'], stages=["Staging"])[-1]
    # search for the production version
    latest_prod_info = client.get_latest_versions(
        name=exp_info['model_name'], stages=["Production"])[-1]

    stage_run_metadata = client.get_run(run_id=latest_stage_info.run_id)

    if latest_prod_info:
        prod_run_metadata = client.get_run(run_id=latest_prod_info.run_id)

        # Compare their metrics and if latest staging model is better then it is pushed to production stage
        if stage_run_metadata['metrics']['c_index'] > prod_run_metadata['metrics']['c_index']:
            client.transition_model_version_stage(
                name=exp_info['model_name'],
                version=latest_stage_info.version,
                stage="Production",
                archive_existing_versions=True)
    else:
        client.transition_model_version_stage(
            name=exp_info['model_name'],
            version=latest_stage_info.version,
            stage="Production",
            archive_existing_versions=True)


if __name__ == "__main__":
    model_search()
