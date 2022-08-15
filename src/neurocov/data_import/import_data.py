import warnings
from datetime import date
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
from connectome_plasticity_project.managers.subjects.process_subjects import SubjectsManager
from tqdm import tqdm

warnings.filterwarnings("ignore", message="The frame.append method is deprecated")
warnings.filterwarnings("ignore", message="DataFrame is highly fragmented.")
warnings.filterwarnings("ignore", message="Cell J199 is marked")


MRI_TABLE_COLUMNS_TRANSFORM = {
    "ID": "ID Number",
    "Height": "height",
    "Weight": "weight",
    "Study": "study",
    "Group": "group",
    "Condition": "condition",
}
DATABASE_COLUMNS_TRANSFORM = {
    "ID Number": "id_number",
    "ID": "database_id",
    "Questionnaire ID": "questionnaire_id",
    "First Name": "first_name",
    "Last Name": "last_name",
    "Date Of Birth": "dob",
    "Dominant Hand": "dominant_hand",
    "Sex": "sex",
}
MRI_QUESTIONNAIRE_MAPPING = {
    "sex": "Sex",
    "age": "Age (years)",
    "weight": "Weight (kg)",
    "height": "Height (cm)",
    "dominant_hand": "Dominant Hand",
}
MRI_ADDITIONS = {"study": "Study", "group": "Group", "condition": "Condition"}
BEGINNING_OF_TIME = pd.to_datetime("2000-01-01")

QUESTIONNAIRE_PATH = "/home/groot/Projects/PhD/papers/covariates-in-neuroimaging/data/questionnaire.csv"


def calculate_age(birth):
    today = date.today()
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


def split_sessions(data: pd.DataFrame, subset_column: str, drop_single_session: bool = True):
    before = data.groupby(("subject_details", "participant")).first()
    after = data.groupby(("subject_details", "participant")).last()
    if drop_single_session:
        dropped_out = before[("session_details", "timestamp")] == after[("session_details", "timestamp")]
        before = before.loc[~dropped_out]
        after = after.loc[~dropped_out]
    before_data, after_data = before[subset_column], after[subset_column]
    return before_data, after_data


def get_mri_subjects(
    information_dir: Union[str, Path] = "/home/groot/Projects/PhD/connectomeplasticity/data/subjects",
    bids_dir: Union[str, Path] = "/media/groot/Yalla/ConnectomePlasticity/MRI/rawdata",
):
    s = SubjectsManager(information_dir, bids_dir=bids_dir, validate_fieldmaps=False, fix_bids=False)
    mri_table, database_ids = s.mri_table, s.databse_ids
    mri_table = mri_table.rename(columns=MRI_TABLE_COLUMNS_TRANSFORM)
    subjects = mri_table.merge(database_ids.reset_index(), on="ID Number", how="outer")
    subjects = subjects.rename(columns=DATABASE_COLUMNS_TRANSFORM)
    columns_to_drop = [
        col
        for col in subjects.columns
        if (col not in MRI_TABLE_COLUMNS_TRANSFORM.values()) and (col not in DATABASE_COLUMNS_TRANSFORM.values())
    ]
    subjects = subjects.drop(columns=columns_to_drop)
    subjects["dob"] = subjects["dob"].apply(pd.to_datetime)
    subjects["age"] = subjects["dob"].apply(calculate_age)
    subjects = subjects.set_index("database_id")
    subjects = subjects[~subjects.index.duplicated(keep="first")]
    return subjects


def get_questionnaire_subjects(questionnaire_path: str = QUESTIONNAIRE_PATH):
    subjects = pd.read_csv(questionnaire_path, index_col=0)
    cols = pd.MultiIndex.from_product([["questionnaire"], subjects.columns])
    subjects.columns = cols
    return subjects.set_index(subjects.index.astype(str))


def get_available_subjects(
    questionnaire_path: str = QUESTIONNAIRE_PATH,
    information_dir: Union[str, Path] = "/home/groot/Projects/PhD/connectomeplasticity/data/subjects",
    bids_dir: Union[str, Path] = "/media/groot/Yalla/ConnectomePlasticity/MRI/rawdata",
):
    mri_subjects = get_mri_subjects(information_dir, bids_dir)
    questionnaire_subjects = get_questionnaire_subjects(questionnaire_path)
    missing_subjects = fill_missing_subjects(questionnaire_subjects, mri_subjects)
    return missing_subjects


def fill_missing_subjects(questionnaire_subjects: pd.DataFrame, mri_subjects: pd.DataFrame) -> pd.DataFrame:
    missing_subjects = [i for i in mri_subjects.index if i not in questionnaire_subjects.index]
    for i in missing_subjects:
        for key, val in MRI_QUESTIONNAIRE_MAPPING.items():
            questionnaire_subjects.loc[i, ("questionnaire", val)] = mri_subjects.loc[i, key]
    for i in mri_subjects.index:
        for key, col in MRI_ADDITIONS.items():
            value = mri_subjects.loc[i, key]
            questionnaire_subjects.loc[i, ("questionnaire", col)] = (
                value.capitalize().replace("Lerner", "Learner") if isinstance(value, str) else value
            )
    return questionnaire_subjects


def collect_mr_data(
    qsiprep_dir: Union[str, Path],
    subjects: pd.DataFrame,
    parcellation_scheme: str = "brainnetome",
    parcellation_type: str = "wholeBrain",
    acquisition: str = "dt",
    reconstruction_software: str = "dipy",
    measure: str = np.nanmean,
) -> pd.DataFrame:
    data = pd.DataFrame()
    missing_subjects = []
    for fname in tqdm(
        Path(qsiprep_dir).rglob(
            f"{reconstruction_software}/*acq-{acquisition}*label-{parcellation_type}*_meas-{measure.__name__}_atlas-{parcellation_scheme}_dseg.pickle"  # noqa
        )
    ):

        subj_name = fname.name.split("_")[0].split("-")[-1]
        tmp_data = pd.read_pickle(fname)
        if subj_name in subjects.index.tolist():
            tmp_data[subjects.columns] = subjects.loc[subj_name]
            # for col in subjects.columns:
            #     tmp_data[("subject_details", col)] = subjects.loc[subj_name, col]
        else:
            missing_subjects.append(subj_name)
        data = pd.concat([data, tmp_data])
    if missing_subjects:
        warnings.warn(f"\nCould not locate the following subjects:\n{list(set(missing_subjects))}")
    return data


def restructure_data(data: pd.DataFrame, min_sessions: int = 2):
    data.index.names = ["participant", "session", "metric"]
    print("Removing subjects with less than 2 sessions")
    all_subjects = list(set(data.index.get_level_values(0)))
    available_subjects = [i for i in all_subjects if data.loc[i].shape[0] >= min_sessions]
    valid_data = data.loc[available_subjects]
    print(f"Removed {len(all_subjects) - len(available_subjects)} subjects")
    print(f"Found a total of {len(available_subjects)} subjects")
    valid_data.reset_index(inplace=True)
    valid_data["session"] = valid_data["session"].apply(pd.to_datetime)
    valid_data[("session_details", "year")] = valid_data["session"].dt.year
    valid_data[("session_details", "month")] = valid_data["session"].dt.month
    valid_data[("session_details", "day_in_month")] = valid_data["session"].dt.day
    valid_data[("session_details", "day_in_week")] = valid_data["session"].dt.dayofweek
    valid_data[("session_details", "hour")] = valid_data["session"].dt.hour
    valid_data[("session_details", "numeric_time")] = (valid_data["session"] - BEGINNING_OF_TIME).dt.seconds

    valid_data[("session_details", "timestamp")] = valid_data["session"]
    valid_data[("questionnaire", "participant")] = valid_data["participant"]
    valid_data.drop(["participant", "session"], axis=1, inplace=True)
    return valid_data


def get_all_data(
    qsiprep_dir: Union[str, Path],
    # information_dir: Union[str, Path] = "/home/groot/Projects/PhD/connectomeplasticity/data/subjects",
    # bids_dir: Union[str, Path] = "/media/groot/Yalla/ConnectomePlasticity/MRI/rawdata",
    parcellation_scheme: str = "brainnetome",
    parcellation_type: str = "wholeBrain",
    acquisition: str = "dt",
    reconstruction_software: str = "dipy",
    measure: str = np.nanmean,
    # columns_to_include: list = ["group", "condition", "height", "weight", "sex", "dob", "age", "dominant_hand"],
):
    # subjects = get_available_subjects(information_dir=information_dir, bids_dir=bids_dir)
    subjects = get_available_subjects()
    data = collect_mr_data(qsiprep_dir, subjects, parcellation_scheme, parcellation_type, acquisition, reconstruction_software, measure)
    data = restructure_data(data)
    return data
