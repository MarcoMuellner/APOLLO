# standard imports
import pytest
import os
import re
# scientific imports
import numpy as np
# project imports
from res.conf_file_str import fits_flux_column, fits_time_column, fits_hdulist_column, ascii_skiprows, ascii_use_cols
from readerWriter.file_reader import load_file, check_file_exists, load_fits_file, load_ascii_file, \
    transpose_if_necessary

pre_path = re.findall(r'.+\/LCA\/', os.getcwd())[0]
test_file_dir = f"{pre_path}tests/testFiles/"


def test_transpose_if_necessary():
    x = np.linspace(0, 100, 1000)
    y = np.random.normal(5, 2, 1000)

    assert y.shape == transpose_if_necessary(y).shape
    assert x.shape == transpose_if_necessary(x).shape

    t_arr = np.array((x, y)).T
    arr = np.array((x, y))

    assert arr.shape == transpose_if_necessary(t_arr).shape
    assert np.all(np.equal(arr, transpose_if_necessary(t_arr)))
    assert arr.shape == transpose_if_necessary(arr).shape
    assert np.all(np.equal(arr, transpose_if_necessary(arr)))


def test_check_file_exists():
    with pytest.raises(FileNotFoundError):
        check_file_exists("does/not/exist/exist.txt")

    with pytest.raises(FileNotFoundError):
        check_file_exists(test_file_dir)

    check_file_exists(f"{test_file_dir}YoungStar.dat.txt")


@pytest.mark.parametrize("file_name", [("YoungStar.dat.txt", (0, 10)), ("Lightcurve.txt", (0, 1))])
def test_load_ascii_file(file_name):
    if file_name[0] == "YoungStar.dat.txt":
        with pytest.raises(ValueError):
            load_ascii_file(f"{test_file_dir}{file_name[0]}", {})

    data = load_ascii_file(f"{test_file_dir}{file_name[0]}", {ascii_skiprows: 1, ascii_use_cols: file_name[1]})
    assert len(transpose_if_necessary(data)) == 2


@pytest.mark.parametrize("file_name", [("fits_lightcurve_without_columns.fits", {fits_hdulist_column: 0}),
                                       ("fits_lightcurve_with_columns.fits",
                                        {fits_hdulist_column: 1, fits_flux_column: 'FCOR',
                                         fits_time_column: 'TIME'}),
                                       ])
def test_load_fits_file(file_name):
    with pytest.raises(AttributeError):
        load_fits_file(f"{test_file_dir}{file_name[0]}", {fits_hdulist_column: "dummy"})

    if len(file_name[1]) == 3:
        with pytest.raises(AttributeError):
            load_fits_file(f"{test_file_dir}{file_name[0]}", {fits_hdulist_column: file_name[1][fits_hdulist_column]})

    fits_data = load_fits_file(f"{test_file_dir}{file_name[0]}", file_name[1])

    assert len(transpose_if_necessary(fits_data)) == 2


@pytest.mark.parametrize("file_name", [("YoungStar.dat.txt", {ascii_skiprows: 1, ascii_use_cols: (0, 10)}),
                                       ("Lightcurve.txt", {ascii_skiprows: 1, ascii_use_cols: (0, 1)}),
                                       ("fits_lightcurve_without_columns.fits", {fits_hdulist_column: 0}),
                                       ("fits_lightcurve_with_columns.fits",
                                        {fits_hdulist_column: 1, fits_flux_column: 'FCOR',
                                         fits_time_column: 'TIME'}), ])
def test_load_file(file_name):
    data = load_file(f"{test_file_dir}{file_name[0]}", file_name[1])
    assert len(transpose_if_necessary(data)) == 2
