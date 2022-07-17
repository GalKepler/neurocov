import os
from pathlib import Path
from typing import Union

import nibabel as nib
import numpy as np
import pandas as pd
from mayavi import mlab
from surfer import Brain
from surfer import project_volume_data
from tqdm import tqdm

NII_TO_SURFACE_REG_FILE = os.path.join(os.environ["FREESURFER_HOME"], "average/mni152.register.dat")


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


def nifti_to_surface_png(nifti_path: Union[Path, str], out_file: Union[Path, str]) -> None:
    """
    Convert a nifti image to a surface plot.

    Parameters
    ----------
    nifti_path : Path
        Path to the nifti image.
    out_file : Path
        Path to the output file.
    """
    """Bring up the visualization"""
    nifti_img = nib.load(nifti_path)
    # vmax = np.percentile(nifti_img.get_fdata(), 90)
    vmax = np.abs(nifti_img.get_fdata()).max()
    fig = [mlab.figure(size=(1200, 1200)) for _ in range(4)]
    brain = Brain("fsaverage", "split", "pial", figure=fig, views=["lat", "med"], background="white")
    brain.set_distance(400)
    surf_data_lh = np.nan_to_num(project_volume_data(nifti_path, "lh", NII_TO_SURFACE_REG_FILE))

    surf_data_rh = np.nan_to_num(project_volume_data(nifti_path, "rh", NII_TO_SURFACE_REG_FILE))

    brain.add_data(surf_data_lh, 0, vmax, center=0, hemi="lh", colorbar=True, colormap="RdBu_r")
    brain.add_data(surf_data_rh, 0, vmax, center=0, hemi="rh", colorbar=True, colormap="RdBu_r")

    brain.scale_data_colormap(0, vmax / 2, vmax, transparent=False, center=0)

    seed_coords = (-45, -67, 36)
    brain.add_foci(seed_coords, map_surface="white", hemi="lh")
    brain.save_image(out_file, mode="rgba")
    mlab.close(all=True)
