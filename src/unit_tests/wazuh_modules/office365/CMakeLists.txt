# Copyright (C) 2015-2021, Wazuh Inc.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License (version 2) as published by the FSF - Free Software
# Foundation.

#include wrappers
include(${SRC_FOLDER}/unit_tests/wrappers/wazuh/shared/shared.cmake)

# Tests list and flags
list(APPEND tests_names "test_wm_office365")
list(APPEND tests_flags "-Wl,--wrap,access -Wl,--wrap,wurl_http_request \
                        -Wl,--wrap,wurl_free_response -Wl,--wrap,wm_sendmsg -Wl,--wrap,strftime -Wl,--wrap,localtime_r \
                        -Wl,--wrap,wm_state_io -Wl,--wrap,time -Wl,--wrap,StartMQ ${DEBUG_OP_WRAPPERS}")

list(APPEND use_shared_libs 1)

list(APPEND shared_libs "../scheduling/wmodules_scheduling_helpers.h")
list(APPEND shared_libs "../scheduling/wmodules_scheduling_helpers.c")

# Generate wazuh modules library
file(GLOB office365 ../../../wazuh_modules/*.o)
list(REMOVE_ITEM office365 ../../../wazuh_modules/main.o)

add_library(OFFICE365_O STATIC ${office365})

set_source_files_properties(
  ${office365}
  PROPERTIES
  EXTERNAL_OBJECT true
  GENERATED true
  )

set_target_properties(
  OFFICE365_O
  PROPERTIES
  LINKER_LANGUAGE C
  )

target_link_libraries(OFFICE365_O ${WAZUHLIB} ${WAZUHEXT} -lpthread)


# Compiling tests
list(LENGTH tests_names count)
math(EXPR count "${count} - 1")
foreach(counter RANGE ${count})
    list(GET tests_names ${counter} test_name)
    list(GET tests_flags ${counter} test_flags)
    list(GET use_shared_libs ${counter} use_libs)

    if(use_libs EQUAL "1")
      add_executable(${test_name} ${test_name}.c ${shared_libs})
    else ()
      add_executable(${test_name} ${test_name}.c)
    endif()

    if(${TARGET} STREQUAL "server")
        target_link_libraries(
            ${test_name}
            ${WAZUHLIB}
            ${WAZUHEXT}
            OFFICE365_O
            -lcmocka
            -ldl
            -fprofile-arcs
            -ftest-coverage
        )
    else()
        target_link_libraries(
            ${test_name}
            ${TEST_DEPS}
        )
    endif()

    if(NOT test_flags STREQUAL " ")
        target_link_libraries(
            ${test_name}
            ${test_flags}
        )
    endif()
    add_test(NAME ${test_name} COMMAND ${test_name})
endforeach()
