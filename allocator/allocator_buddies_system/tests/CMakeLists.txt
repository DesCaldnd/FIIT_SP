add_executable(
        sys_prog_allctr_allctr_bdds_sstm_tests
        allocator_buddies_system_tests.cpp)

target_link_libraries(
        sys_prog_allctr_allctr_bdds_sstm_tests
        PRIVATE
        gtest_main)
target_link_libraries(
        sys_prog_allctr_allctr_bdds_sstm_tests
        PRIVATE
        sys_prog_allctr_allctr_bdds_sstm)

gtest_discover_tests(
        sys_prog_allctr_allctr_bdds_sstm_tests
        TEST_PREFIX "sys_prog_allctr_allctr_bdds_sstm_tests."
        DISCOVERY_TIMEOUT 60)
