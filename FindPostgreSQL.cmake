find_path(PostgreSQL_INCLUDE_DIR NAMES postgres_ext.h PATHS ${CONAN_INCLUDE_DIRS_LIBPQ} NO_CMAKE_FIND_ROOT_PATH)
find_library(PostgreSQL_LIBRARY NAMES pq libpq PATHS ${CONAN_LIB_DIRS_LIBPQ} NO_CMAKE_FIND_ROOT_PATH)

foreach(library ${CONAN_LIBS_LIBPQ})
    find_library(found_library_${library} NAMES ${library} PATHS ${CONAN_LIB_DIRS_LIBPQ} NO_CMAKE_FIND_ROOT_PATH)
    if (found_library_${library})
        list(APPEND PostgreSQL_LIBRARIES ${found_library_${library}})
    endif()
endforeach()

MESSAGE("** PostgreSQL ALREADY FOUND BY CONAN!")
SET(PostgreSQL_FOUND TRUE)
MESSAGE("** FOUND PostgreSQL:  ${PostgreSQL_LIBRARY}")
MESSAGE("** FOUND PostgreSQL INCLUDE:  ${PostgreSQL_INCLUDE_DIR}")

set(PostgreSQL_INCLUDE_DIRS ${PostgreSQL_INCLUDE_DIR})
if(WIN32)
    list(APPEND PostgreSQL_LIBRARIES ws2_32 secur32 advapi32 shell32)
endif()

message(STATUS "PostgreSQL_LIBRARIES: ${PostgreSQL_LIBRARIES}")

mark_as_advanced(PostgreSQL_ROOT PostgreSQL_LIBRARY PostgreSQL_INCLUDE_DIR)

set(PostgreSQL_MAJOR_VERSION "9")
set(PostgreSQL_MINOR_VERSION "6")
set(PostgreSQL_PATCH_VERSION "9")
