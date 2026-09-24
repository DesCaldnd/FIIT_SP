add_executable(
        sys_prog_allctr_allctr_bndr_tgs_tests
        allocator_boundary_tags_tests.cpp)

target_link_libraries(
        sys_prog_allctr_allctr_bndr_tgs_tests
        PRIVATE
        gtest_main)
target_link_libraries(
        sys_prog_allctr_allctr_bndr_tgs_tests
        PRIVATE
        sys_prog_allctr_allctr_bndr_tgs)

gtest_discover_tests(
        sys_prog_allctr_allctr_bndr_tgs_tests
        TEST_PREFIX "sys_prog_allctr_allctr_bndr_tgs_tests."
        DISCOVERY_TIMEOUT 60)
