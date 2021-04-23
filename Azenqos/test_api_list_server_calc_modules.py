import sys
import azq_server_api


def test(server, user, passwd, lhl):
    print("server", server)
    print("user", user)
    print("passwd", passwd)
    token = azq_server_api.api_login_get_token(server, user, passwd)
    assert token
    ret_dict = azq_server_api.api_py_eval_get_parsed_ret_dict(
        server, token, lhl, "list_modules_with_process_cell_func.run()"
    )
    # print("ret_dict: {}".format(ret_dict))
    assert ret_dict
    assert ret_dict["ret_type"] == "<type 'dict'>"
    assert isinstance(ret_dict["ret"], dict)
    for test_mod in ["plot_param", "rach_ssr", "plot_histogram"]:
        func_def = ret_dict["ret"][test_mod]
        print("mod: {} process_cell_func_def: {}".format(test_mod, func_def))


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("argc too short so using defaults")
        # 474974357483649200 is log_hash for ../example_logs/nr_exynos_drive1/354569110588585-18_08_2020-13_54_22.azm
        # 345757788188057704 is log_hash for ../example_logs/lte_benchmark/357008080503008-26_08_2020-16_18_08.azm
        test(
            server="https://test0.azenqos.com",
            user="trial_admin",
            passwd="3.14isnotpina",
            lhl="474974357483649200,345757788188057704",
        )
    else:
        test(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])