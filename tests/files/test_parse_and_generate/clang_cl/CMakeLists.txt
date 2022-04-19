cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/gen)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/obj/base/base_static)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/obj/base)

set_source_files_properties(${SOURCE_DIR}/base_switches.cc PROPERTIES COMPILE_OPTIONS
    "/showIncludes;-imsvcC:\\\\Program Files (x86)\\\\Microsoft Visual Studio\\\\2017\\\\Professional\\\\VC\\\\Tools\\\\MSVC\\\\14.16.27023\\\\ATLMFC\\\\include;-imsvcC:\\\\Program Files (x86)\\\\Microsoft Visual Studio\\\\2017\\\\Professional\\\\VC\\\\Tools\\\\MSVC\\\\14.16.27023\\\\include;-imsvcC:\\\\Program Files (x86)\\\\Windows Kits\\\\NETFXSDK\\\\4.6.1\\\\include\\\\um;-imsvcC:\\\\Program Files (x86)\\\\Windows Kits\\\\10\\\\include\\\\10.0.17763.0\\\\ucrt;-imsvcC:\\\\Program Files (x86)\\\\Windows Kits\\\\10\\\\include\\\\10.0.17763.0\\\\shared;-imsvcC:\\\\Program Files (x86)\\\\Windows Kits\\\\10\\\\include\\\\10.0.17763.0\\\\um;-imsvcC:\\\\Program Files (x86)\\\\Windows Kits\\\\10\\\\include\\\\10.0.17763.0\\\\winrt;-imsvcC:\\\\Program Files (x86)\\\\Windows Kits\\\\10\\\\include\\\\10.0.17763.0\\\\cppwinrt;-DUSE_AURA=1;-DNO_TCMALLOC;-DFULL_SAFE_BROWSING;-DSAFE_BROWSING_CSD;-DSAFE_BROWSING_DB_LOCAL;-DOFFICIAL_BUILD;-DCHROMIUM_BUILD;-DCR_CLANG_REVISION=\"351477-1\";-D_HAS_NODISCARD;-D_HAS_EXCEPTIONS=0;-D__STD_C;-D_CRT_RAND_S;-D_CRT_SECURE_NO_DEPRECATE;-D_SCL_SECURE_NO_DEPRECATE;-D_ATL_NO_OPENGL;-D_WINDOWS;-DCERT_CHAIN_PARA_HAS_EXTRA_FIELDS;-DPSAPI_VERSION=2;-DWIN32;-D_SECURE_ATL;-D_USING_V110_SDK71_;-DWINAPI_FAMILY=WINAPI_FAMILY_DESKTOP_APP;-DWIN32_LEAN_AND_MEAN;-DNOMINMAX;-D_UNICODE;-DUNICODE;-DNTDDI_VERSION=0x0A000002;-D_WIN32_WINNT=0x0A00;-DWINVER=0x0A00;-DNVALGRIND;-DDYNAMIC_ANNOTATIONS_ENABLED=0;/utf-8;/X;-fcolor-diagnostics;-fmerge-all-constants;SHELL:-Xclang -mllvm;SHELL:-Xclang -instcombine-lower-dbg-declare=0;-no-canonical-prefixes;-fcomplete-member-pointers;/Gy;/FS;/bigobj;/d2FastFail;/Zc:sizedDealloc-;-fmsc-version=1911;/W4;-Wimplicit-fallthrough;-Wthread-safety;/WX;/wd4091;/wd4127;/wd4251;/wd4275;/wd4312;/wd4324;/wd4351;/wd4355;/wd4503;/wd4589;/wd4611;/wd4100;/wd4121;/wd4244;/wd4505;/wd4510;/wd4512;/wd4610;/wd4838;/wd4995;/wd4996;/wd4456;/wd4457;/wd4458;/wd4459;/wd4200;/wd4201;/wd4204;/wd4221;/wd4245;/wd4267;/wd4305;/wd4389;/wd4702;/wd4701;/wd4703;/wd4661;/wd4706;/wd4715;-Wno-missing-field-initializers;-Wno-unused-parameter;-Wno-c++11-narrowing;-Wno-unneeded-internal-declaration;-Wno-undefined-var-template;-Wno-nonportable-include-path;-Wno-ignored-pragma-optimize;-fno-standalone-debug;/MT$<$<CONFIG:Debug>:d>;-Wheader-hygiene;-Wstring-conversion;-Wtautological-overlap-compare;/Ob2;/Oy-;/Zc:inline;/Gw;/wd4577;/GR-"
)
set_source_files_properties(${SOURCE_DIR}/base_switches.cc PROPERTIES INCLUDE_DIRECTORIES "${SOURCE_DIR};${CMAKE_CURRENT_BINARY_DIR}/gen")
add_library(base_static.static STATIC ${SOURCE_DIR}/base_switches.cc)
target_link_options(base_static.static PRIVATE /ignore:4221 /llvmlibthin)
set_target_properties(base_static.static PROPERTIES OUTPUT_NAME base_static)
set_target_output_subdir(base_static.static ARCHIVE_OUTPUT_DIRECTORY obj/base)
