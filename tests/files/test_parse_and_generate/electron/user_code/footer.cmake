
file(TO_NATIVE_PATH ${ELECTRON_SOURCE_DIR} ELECTRON_SOURCE_DIR_NATIVE)
string(REPLACE "\\" "\\\\" ELECTRON_SOURCE_DIR_NATIVE ${ELECTRON_SOURCE_DIR_NATIVE})
configure_file(prebuilt/gen/ui/resources/ui_unscaled_resources.rc
               ${CMAKE_CURRENT_BINARY_DIR}/gen/ui/resources/ui_unscaled_resources.rc
               @ONLY)

set(OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/installed)
file(MAKE_DIRECTORY ${OUTPUT_DIRECTORY})

if(NOT DEFINED ARCHIVE_OUTPUT_DIRECTORY)
    set(ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
endif()

set(ELECTRON_TARGETS
    electron
)

install(TARGETS ${ELECTRON_TARGETS} DESTINATION .)
install(FILES
    ${CMAKE_CURRENT_LIST_DIR}/../file_list.cmake
    DESTINATION .)

add_custom_target(external.electron.install
    ${CMAKE_COMMAND}
        -DCMAKE_INSTALL_PREFIX=${OUTPUT_DIRECTORY}
        -DBUILD_TYPE=$<CONFIG>
        -P ${CMAKE_CURRENT_BINARY_DIR}/cmake_install.cmake
)

add_tarball_target(electron ${OUTPUT_DIRECTORY} ${ARCHIVE_OUTPUT_DIRECTORY})

add_custom_target(external.electron.build)

add_dependencies(external.electron.install ${ELECTRON_TARGETS})
add_dependencies(external.electron.build external.electron.install)

add_dependencies(external.electron.tarball external.electron.build)
