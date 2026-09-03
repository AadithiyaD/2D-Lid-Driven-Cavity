cmake_minimum_required(VERSION 3.10)  # Minimum CMake version

# Set C++ standard (C++11 or later for Eigen)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

# Find required packages
find_package(Eigen3 REQUIRED) 

# Add your executable and its source files
add_executable(step11
    src/step11.cpp
    src/myMathFuncs/discretizationSchemes.cpp
    src/myMathFuncs/operators.cpp
)

# The link tells the compiler which files and libraries to look for definitions
target_link_libraries(step11                # The name of your executable or library (e.g., `step11`)
    PRIVATE                                 # Scope: Only this step11 needs these libraries, and not other files taht depend on step11
    Eigen3::Eigen                           # This Eigen3::Eigen is a target created by find_package(Eigen3)
)

# Similar structure to target link libraries 
# The drectory include tells the compiler where to look to find the libraries needed
target_include_directories(step11
    PRIVATE
    ${EIGEN3_INCLUDE_DIRS}
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)
