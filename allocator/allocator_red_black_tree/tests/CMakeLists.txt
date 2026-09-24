add_executable(
        sys_prog_allctr_allctr_rb_tr_tests
        allocator_red_black_tree_tests.cpp)

target_link_libraries(
        sys_prog_allctr_allctr_rb_tr_tests
        PRIVATE
        gtest_main)
target_link_libraries(
        sys_prog_allctr_allctr_rb_tr_tests
        PRIVATE
        sys_prog_allctr_allctr_rb_tr)

gtest_discover_tests(
        sys_prog_allctr_allctr_rb_tr_tests
        TEST_PREFIX "sys_prog_allctr_allctr_rb_tr_tests."
        DISCOVERY_TIMEOUT 60)
