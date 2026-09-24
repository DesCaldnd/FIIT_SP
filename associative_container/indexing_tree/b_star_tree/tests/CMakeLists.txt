add_executable(
        sys_prog_assctv_cntnr_indxng_tr_b_str_tr_tests
        b_star_tree_tests.cpp)

target_link_libraries(
        sys_prog_assctv_cntnr_indxng_tr_b_str_tr_tests
        PRIVATE
        gtest_main)
target_link_libraries(
        sys_prog_assctv_cntnr_indxng_tr_b_str_tr_tests
        PRIVATE
        sys_prog_assctv_cntnr_indxng_tr_b_str_tr)

gtest_discover_tests(
        sys_prog_assctv_cntnr_indxng_tr_b_str_tr_tests
        TEST_PREFIX "sys_prog_assctv_cntnr_indxng_tr_b_str_tr_tests."
        DISCOVERY_TIMEOUT 60)
