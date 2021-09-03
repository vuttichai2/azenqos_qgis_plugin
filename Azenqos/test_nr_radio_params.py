import integration_test_helpers
import nr_query
import contextlib

def test():
    azmfp = "../example_logs/nr_exynos_drive1/354569110588585-18_08_2020-13_54_22.azm"
    # azmfp = "../example_logs/nr_table_restructure/354255815642535-14_05_2021-18_57_10.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with contextlib.closing(integration_test_helpers.get_dbcon(dbfp)) as dbcon:
        df = nr_query.get_nr_radio_params_disp_df_old(dbcon, "2020-08-18 13:48:02.356")
        print("df.head():\n %s" % df.head(20))
        assert df.iloc[3, 1] == 41


if __name__ == "__main__":
    test()
