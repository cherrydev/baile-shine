# Create an INTERFACE library for our C module.
add_library(usermod_lfilter INTERFACE)

# Add our source files to the lib
target_sources(usermod_lfilter INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/examplemodule.c
    ${CMAKE_CURRENT_LIST_DIR}/filter_util.c
    ${CMAKE_CURRENT_LIST_DIR}/bpm_filter_chain.c
)

set_source_files_properties(
    ${CMAKE_CURRENT_LIST_DIR}/filter_util.c
    PROPERTIES COMPILE_FLAGS
    "-O4 -Wno-unused-variable"
)

set_source_files_properties(
    ${CMAKE_CURRENT_LIST_DIR}/bpm_filter_chain.c
    PROPERTIES COMPILE_FLAGS
    -O4
)

#target_compile_options(usermod_lfilter INTERFACE
#    -O2
#)

# Add the current directory as an include directory.
target_include_directories(usermod_lfilter INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}
)

# Link our INTERFACE library to the usermod target.
target_link_libraries(usermod INTERFACE usermod_lfilter)
