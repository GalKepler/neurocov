from pathlib import Path
import nibabel as nib
import pandas as pd
import numpy as np
from typing import Union
from tqdm import tqdm


def df_to_nifti(df: pd.DataFrame, labeled_img_path: Union[Path, str], value_column: str, match_by: str = "Label") -> nib.Nifti1Image:
    """
    Convert a dataframe to a nifti image.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to convert.
    labeled_img_path : Path
        Path to the labeled image.
    value_column : str
        Column name of the value to use.
    match_by : str
        Column name to match the dataframe to the labeled image, by default "Label".

    Returns
    -------
    nib.Nifti1Image
        Nifti image with the labels replaced with those in *df*.
    """
    print(
        f"""Converting dataframe to nifti...
    Matching column: {match_by}.
    Value column: {value_column}."""
    )
    labeled_img = nib.load(str(labeled_img_path))
    labeled_img_data = labeled_img.get_fdata()
    template_data = np.zeros_like(labeled_img_data)
    for _, row in tqdm(df.iterrows()):
        label = row[match_by]
        value = row[value_column]
        template_data[labeled_img_data == label] = value
    return nib.Nifti1Image(template_data, labeled_img.affine, labeled_img.header)
