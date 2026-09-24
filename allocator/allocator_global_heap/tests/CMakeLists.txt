add_executable(
        sys_prog_allctr_allctr_glbl_hp_tests
        allocator_global_heap_tests.cpp)

target_link_libraries(
        sys_prog_allctr_allctr_glbl_hp_tests
        PRIVATE
        gtest_main)
target_link_libraries(
        sys_prog_allctr_allctr_glbl_hp_tests
        PRIVATE
        sys_prog_allctr_allctr_glbl_hp)

gtest_discover_tests(
        sys_prog_allctr_allctr_glbl_hp_tests
        TEST_PREFIX "sys_prog_allctr_allctr_glbl_hp_tests."
        DISCOVERY_TIMEOUT 60)
