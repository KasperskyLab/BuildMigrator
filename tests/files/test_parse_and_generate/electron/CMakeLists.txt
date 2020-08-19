cmake_minimum_required(VERSION 3.13)

project(electron LANGUAGES C CXX VERSION 5.0.5)
enable_language(ASM_NASM)
enable_language(RC)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(ELECTRON_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}/source" CACHE PATH "")
set(CMAKE_ASM_YASM_OBJECT_FORMAT win32)
set(CMAKE_ASM_YASM_MACHINE x86)
set(CMAKE_ASM_NASM_OBJECT_FORMAT win32)
set(compile_flags_1
    -DCERT_CHAIN_PARA_HAS_EXTRA_FIELDS
    -DCHROMIUM_BUILD
    -DCR_CLANG_REVISION="351477-1"
    -DDYNAMIC_ANNOTATIONS_ENABLED=0
    -DFULL_SAFE_BROWSING
    -DNOMINMAX
    -DNO_TCMALLOC
    -DNVALGRIND
    -DOFFICIAL_BUILD
    -DPSAPI_VERSION=2
    -DSAFE_BROWSING_CSD
    -DSAFE_BROWSING_DB_LOCAL
    -DUSE_AURA=1
    -DWIN32
    -DWIN32_LEAN_AND_MEAN
    -DWINAPI_FAMILY=WINAPI_FAMILY_DESKTOP_APP
    -DWINVER=0x0A00
    -D_ATL_NO_OPENGL
    -D_CRT_RAND_S
    -D_CRT_SECURE_NO_DEPRECATE
    -D_HAS_EXCEPTIONS=0
    -D_SCL_SECURE_NO_DEPRECATE
    -D_SECURE_ATL
    -D_USING_V110_SDK71_
    -D_WINDOWS
    -D__STD_C
)
set(compile_flags_2
    -DANGLE_DISABLE_TRACE
    -DGLAPI=
    -DGL_API=
    -DGL_APICALL=
    -DGL_GLEXT_PROTOTYPES
    -DNO_SANITIZE_FUNCTION=
    -D_CRT_NONSTDC_NO_DEPRECATE
    -D_CRT_NONSTDC_NO_WARNINGS
    -D_WINDLL
    -D__STDC_CONSTANT_MACROS
    -D__STDC_LIMIT_MACROS
)
set(compile_flags_3
    -DGR_GL_FUNCTION_TYPE=__stdcall
    -DSK_GPU_WORKAROUNDS_HEADER="gpu/config/gpu_driver_bug_workaround_autogen.h"
    -DSK_HAS_JPEG_LIBRARY
    -DSK_HAS_PNG_LIBRARY
    -DSK_HAS_WEBP_LIBRARY
    -DSK_SUPPORT_GPU=1
)
set(compile_flags_4
    -Wno-c++11-narrowing
    -Wno-ignored-pragma-optimize
    -Wno-nonportable-include-path
    -fcomplete-member-pointers
    -fmsc-version=1911
    /Gw
    /Zc:inline
    /Zc:sizedDealloc-
    /bigobj
)
set(include_dirs_1
    ${ELECTRON_SOURCE_DIR}/skia/config
    ${ELECTRON_SOURCE_DIR}/skia/ext
    ${ELECTRON_SOURCE_DIR}/third_party/skia/include/c
    ${ELECTRON_SOURCE_DIR}/third_party/skia/include/codec
    ${ELECTRON_SOURCE_DIR}/third_party/skia/include/config
    ${ELECTRON_SOURCE_DIR}/third_party/skia/include/core
    ${ELECTRON_SOURCE_DIR}/third_party/skia/include/docs
    ${ELECTRON_SOURCE_DIR}/third_party/skia/include/effects
    ${ELECTRON_SOURCE_DIR}/third_party/skia/include/encode
    ${ELECTRON_SOURCE_DIR}/third_party/skia/include/gpu
    ${ELECTRON_SOURCE_DIR}/third_party/skia/include/pathops
    ${ELECTRON_SOURCE_DIR}/third_party/skia/include/ports
    ${ELECTRON_SOURCE_DIR}/third_party/skia/include/utils
    ${ELECTRON_SOURCE_DIR}/third_party/skia/modules/skottie/include
    ${ELECTRON_SOURCE_DIR}/third_party/skia/src/gpu
    ${ELECTRON_SOURCE_DIR}/third_party/skia/src/sksl
)
set(include_dirs_2
    ${CMAKE_CURRENT_BINARY_DIR}/gen
    ${ELECTRON_SOURCE_DIR}
    ${ELECTRON_SOURCE_DIR}/third_party/swiftshader/include
    ${ELECTRON_SOURCE_DIR}/third_party/swiftshader/src
    ${ELECTRON_SOURCE_DIR}/third_party/swiftshader/src/OpenGL
)
language_compile_options(CXX ${compile_flags_1} ${compile_flags_4} /GR-)
language_compile_options(RC ${compile_flags_1})
link_libraries(
    dbghelp
    dnsapi
    msimg32
    odbc32
    odbccp32
    shlwapi
    usp10
    version
    wininet
    winmm
    ws2_32
    delayimp
)
shared_link_options(
    /OPT:REF
    /OPT:ICF
    /INCREMENTAL:NO
    /FIXED:NO
    /OPT:NOLLDTAILMERGE
    /SAFESEH
    /largeaddressaware
    /fastfail
    /NXCOMPAT
    /DYNAMICBASE
    /SUBSYSTEM:CONSOLE,5.01
)
static_library_options(/llvmlibthin)

set(copy_prebuilt_artifacts_DIR prebuilt)
set(copy_prebuilt_artifacts_DEST ${CMAKE_CURRENT_BINARY_DIR})
file(GLOB_RECURSE _files RELATIVE ${CMAKE_CURRENT_LIST_DIR}/${copy_prebuilt_artifacts_DIR} ${copy_prebuilt_artifacts_DIR}/*)
foreach(_f ${_files})
    configure_file(${copy_prebuilt_artifacts_DIR}/${_f} ${copy_prebuilt_artifacts_DEST}/${_f} COPYONLY)
endforeach()
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/swiftshader)

add_library(egl SHARED
    ${ELECTRON_SOURCE_DIR}/third_party/swiftshader/src/Common/SharedLibrary.cpp
    ${ELECTRON_SOURCE_DIR}/third_party/swiftshader/src/OpenGL/libEGL/main.cpp
)
target_compile_options(egl PRIVATE
    -D_CRT_NONSTDC_NO_WARNINGS
    -D_CRT_NONSTDC_NO_DEPRECATE
    -D_WINDLL
    -DNO_SANITIZE_FUNCTION=
    -DANGLE_DISABLE_TRACE
    -DEGL_EGLEXT_PROTOTYPES
    -DEGLAPI=
    /Oi
    -Wno-unused-variable
    /Zc:wchar_t
)
target_include_directories(egl PRIVATE ${include_dirs_2})
set_target_properties(egl PROPERTIES OUTPUT_NAME libEGL)
set_target_properties(egl PROPERTIES ARCHIVE_OUTPUT_NAME libEGL.dll)
set_target_output_subdir(egl RUNTIME_OUTPUT_DIRECTORY swiftshader)
set_target_output_subdir(egl ARCHIVE_OUTPUT_DIRECTORY swiftshader)
set_target_properties(egl PROPERTIES VERSION 5.0.5)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/obj/third_party/swiftshader/src/OpenGL/libGLESv2)

add_library(swiftshader_libglesv2_static.static STATIC
    ${ELECTRON_SOURCE_DIR}/third_party/swiftshader/src/Common/SharedLibrary.cpp
    ${ELECTRON_SOURCE_DIR}/third_party/swiftshader/src/OpenGL/libGLESv2/libGLESv2.cpp
    ${ELECTRON_SOURCE_DIR}/third_party/swiftshader/src/OpenGL/libGLESv2/libGLESv3.cpp
    ${ELECTRON_SOURCE_DIR}/third_party/swiftshader/src/OpenGL/libGLESv2/main.cpp
)
target_compile_options(swiftshader_libglesv2_static.static PRIVATE ${compile_flags_2} /Oi -Wno-unused-variable /Zc:wchar_t)
target_include_directories(swiftshader_libglesv2_static.static PRIVATE ${include_dirs_2})
set_target_properties(swiftshader_libglesv2_static.static PROPERTIES OUTPUT_NAME swiftshader_libGLESv2_static)
set_target_output_subdir(swiftshader_libglesv2_static.static ARCHIVE_OUTPUT_DIRECTORY obj/third_party/swiftshader/src/OpenGL/libGLESv2)
set_target_properties(swiftshader_libglesv2_static.static PROPERTIES VERSION 5.0.5)

add_library(swiftshader_glesv2 SHARED
    ${ELECTRON_SOURCE_DIR}/third_party/swiftshader/src/OpenGL/libGLESv2/entry_points.cpp
    ${ELECTRON_SOURCE_DIR}/third_party/swiftshader/src/OpenGL/libGLESv2/libGLESv2.rc
)
target_link_libraries(swiftshader_glesv2 PRIVATE dxguid swiftshader_libglesv2_static.static)
target_compile_options(swiftshader_glesv2 PRIVATE ${compile_flags_2})
target_include_directories(swiftshader_glesv2 PRIVATE ${include_dirs_2})
target_language_compile_options(swiftshader_glesv2 CXX PRIVATE /Oi -Wno-unused-variable /Zc:wchar_t)
set_target_properties(swiftshader_glesv2 PROPERTIES OUTPUT_NAME libGLESv2)
set_target_properties(swiftshader_glesv2 PROPERTIES ARCHIVE_OUTPUT_NAME libGLESv2.dll)
set_target_output_subdir(swiftshader_glesv2 RUNTIME_OUTPUT_DIRECTORY swiftshader)
set_target_output_subdir(swiftshader_glesv2 ARCHIVE_OUTPUT_DIRECTORY swiftshader)
set_target_properties(swiftshader_glesv2 PROPERTIES VERSION 5.0.5)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/gen/protoc_out)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/gen/third_party/webrtc)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/gen/v8/include)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/gen/third_party/perfetto/protos)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/obj/third_party/usrsctp)

add_library(usrsctp.static STATIC
    ${CMAKE_CURRENT_BINARY_DIR}/gen/base/base_jumbo_7.cc
    ${CMAKE_CURRENT_BINARY_DIR}/gen/base/base_jumbo_c.c
)
target_compile_options(usrsctp.static PRIVATE -D_HAS_NODISCARD -D_UNICODE -DUNICODE -DBASE_IMPLEMENTATION)
target_include_directories(usrsctp.static PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}
    ${ELECTRON_SOURCE_DIR}
    ${CMAKE_CURRENT_BINARY_DIR}/gen
)
target_language_compile_options(usrsctp.static C PRIVATE ${compile_flags_1} ${compile_flags_4})
set_target_properties(usrsctp.static PROPERTIES OUTPUT_NAME usrsctp)
set_target_output_subdir(usrsctp.static ARCHIVE_OUTPUT_DIRECTORY obj/third_party/usrsctp)
set_target_properties(usrsctp.static PROPERTIES VERSION 5.0.5)

set_source_files_properties(${ELECTRON_SOURCE_DIR}/third_party/skia/src/opts/SkOpts_hsw.cpp PROPERTIES COMPILE_OPTIONS /arch:AVX2)
set_source_files_properties(${ELECTRON_SOURCE_DIR}/third_party/skia/src/opts/SkOpts_sse42.cpp PROPERTIES COMPILE_OPTIONS "-DSK_CPU_SSE_LEVEL=42;-msse4.2")
set_source_files_properties(${ELECTRON_SOURCE_DIR}/third_party/blink/renderer/platform/heap/asm/SaveRegisters_x86.asm PROPERTIES COMPILE_OPTIONS "-DPREFIX;-DIA32=1")
set_source_files_properties(${ELECTRON_SOURCE_DIR}/third_party/blink/renderer/platform/heap/asm/SaveRegisters_x86.asm PROPERTIES INCLUDE_DIRECTORIES "${CMAKE_CURRENT_BINARY_DIR}")
set_source_files_properties(${ELECTRON_SOURCE_DIR}/electron/atom/browser/resources/win/atom.rc PROPERTIES COMPILE_OPTIONS
    "${compile_flags_3};-DWEBP_EXTERN=extern;-DUSE_EGL;-DTOOLKIT_VIEWS=1;-DATOM_PRODUCT_NAME=\"Electron\";-DATOM_PROJECT_NAME=\"electron\";-DGOOGLE_PROTOBUF_NO_RTTI;-DGOOGLE_PROTOBUF_NO_STATIC_INITIALIZER;-DWEBRTC_NON_STATIC_TRACE_EVENT_HANDLERS=0;-DWEBRTC_CHROMIUM_BUILD;-DWEBRTC_WIN;-DABSL_ALLOCATOR_NOTHROW=1;-DNO_MAIN_THREAD_WRAPPING;-DU_USING_ICU_NAMESPACE=0;-DU_ENABLE_DYLOAD=0;-DUSE_CHROMIUM_ICU=1;-DU_STATIC_IMPLEMENTATION;-DICU_UTIL_DATA_IMPL=ICU_UTIL_DATA_FILE;-DUCHAR_TYPE=wchar_t;-DV8_USE_EXTERNAL_STARTUP_DATA;-DLEVELDB_PLATFORM_CHROMIUM=1;-DDeleteFile=DeleteFileW;-DV8_DEPRECATION_WARNINGS;-DPERFETTO_BUILD_WITH_EMBEDDER;-DPERFETTO_BUILD_WITH_CHROMIUM;-DPERFETTO_FORCE_DLOG=0"
)
set_source_files_properties(${ELECTRON_SOURCE_DIR}/electron/atom/browser/resources/win/atom.rc PROPERTIES INCLUDE_DIRECTORIES
    "${ELECTRON_SOURCE_DIR}/electron;${ELECTRON_SOURCE_DIR}/third_party/libwebp/src;${ELECTRON_SOURCE_DIR}/third_party/wtl/include;${ELECTRON_SOURCE_DIR}/third_party/libyuv/include;${ELECTRON_SOURCE_DIR}/third_party/khronos;${ELECTRON_SOURCE_DIR}/gpu;${ELECTRON_SOURCE_DIR}/third_party/jsoncpp/overrides/include;${ELECTRON_SOURCE_DIR}/third_party/jsoncpp/source/include;${ELECTRON_SOURCE_DIR}/third_party/breakpad/breakpad/src;${ELECTRON_SOURCE_DIR}/third_party/protobuf/src;${CMAKE_CURRENT_BINARY_DIR}/gen/protoc_out;${ELECTRON_SOURCE_DIR}/third_party/boringssl/src/include;${ELECTRON_SOURCE_DIR}/third_party/webrtc_overrides;${ELECTRON_SOURCE_DIR}/third_party/webrtc;${CMAKE_CURRENT_BINARY_DIR}/gen/third_party/webrtc;${ELECTRON_SOURCE_DIR}/third_party/abseil-cpp;${ELECTRON_SOURCE_DIR}/third_party/ced/src;${ELECTRON_SOURCE_DIR}/third_party/icu/source/common;${ELECTRON_SOURCE_DIR}/third_party/icu/source/i18n;${ELECTRON_SOURCE_DIR}/third_party/libwebm/source;${ELECTRON_SOURCE_DIR}/third_party/leveldatabase;${ELECTRON_SOURCE_DIR}/third_party/leveldatabase/src;${ELECTRON_SOURCE_DIR}/third_party/leveldatabase/src/include;${ELECTRON_SOURCE_DIR}/v8/include;${CMAKE_CURRENT_BINARY_DIR}/gen/v8/include;${ELECTRON_SOURCE_DIR}/third_party/perfetto/include;${CMAKE_CURRENT_BINARY_DIR}/gen/third_party/perfetto/protos;${ELECTRON_SOURCE_DIR}/testing/gtest/include;${include_dirs_1}"
)
add_library(electron SHARED
    ${ELECTRON_SOURCE_DIR}/electron/atom/browser/resources/win/disable_window_filtering.manifest
    ${ELECTRON_SOURCE_DIR}/electron/atom/browser/resources/win/dpi_aware.manifest
    ${ELECTRON_SOURCE_DIR}/build/win/as_invoker.manifest
    ${ELECTRON_SOURCE_DIR}/build/win/common_controls.manifest
    ${ELECTRON_SOURCE_DIR}/build/win/compatibility.manifest
    ${ELECTRON_SOURCE_DIR}/third_party/skia/src/opts/SkOpts_hsw.cpp
    ${ELECTRON_SOURCE_DIR}/third_party/skia/src/opts/SkOpts_sse42.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/gen/ui/resources/ui_unscaled_resources.rc
    ${ELECTRON_SOURCE_DIR}/third_party/ffmpeg/libavutil/x86/fixed_dsp.asm
    ${ELECTRON_SOURCE_DIR}/electron/atom/browser/resources/win/atom.rc
)
target_link_options(electron PRIVATE
    /DELAYLOAD:api-ms-win-core-winrt-l1-1-0.dll
    /DELAYLOAD:api-ms-win-core-winrt-string-l1-1-0.dll
    /SUBSYSTEM:WINDOWS,5.01
    /DELAYLOAD:cfgmgr32.dll
    /DELAYLOAD:powrprof.dll
    /DELAYLOAD:setupapi.dll
    /DELAYLOAD:BluetoothApis.dll
    /DELAYLOAD:Bthprops.cpl
    /DELAYLOAD:mf.dll
    /DELAYLOAD:mfplat.dll
    /DELAYLOAD:mfreadwrite.dll
)
target_link_libraries(electron PRIVATE
    comctl32
    uiautomationcore
    wtsapi32
    dwmapi
    cfgmgr32
    powrprof
    propsys
    setupapi
    userenv
    wbemuuid
    crypt32
    dhcpcsvc
    iphlpapi
    ncrypt
    rpcrt4
    secur32
    urlmon
    winhttp
    dwrite
    fontsub
    imm32
    d2d1
    d3d10_1
    oleacc
    dxguid
    wevtapi
    Bthprops
    BluetoothApis
    dxgi
    d3d9
    d3d11
    dxva2
    strmiids
    mf
    mfplat
    mfuuid
    mfreadwrite
    winusb
    dinput8
    portabledeviceguids
    sensorsapi
    hid
    wintrust
    netapi32
    ntdsapi
    psapi
    usrsctp.static
)
target_include_directories(electron PRIVATE ${ELECTRON_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR}/gen)
target_language_compile_options(electron ASM_NASM PRIVATE
    -DPREFIX
    -DARCH_X86_32
    -W+error=all
    -DPIC
    -P${ELECTRON_SOURCE_DIR}/third_party/ffmpeg/chromium/config/Chrome/win/ia32/config.asm
)
target_language_compile_options(electron CXX PRIVATE
    ${compile_flags_3}
    -D_UNICODE
    -DUNICODE
    "-DSK_FREETYPE_MINIMUM_RUNTIME_VERSION=(((FREETYPE_MAJOR) * 0x01000000) | ((FREETYPE_MINOR) * 0x00010000) | ((FREETYPE_PATCH) * 0x00000100))"
    -DSKIA_IMPLEMENTATION=1
    -DSK_GAMMA_SRGB
    -DSK_GAMMA_CONTRAST=0.5
    -DSK_DEFAULT_FONT_CACHE_LIMIT=20971520
    -DSK_DEFAULT_FONT_CACHE_COUNT_LIMIT=256
    -D_CRT_NONSTDC_NO_WARNINGS
    -D_CRT_NONSTDC_NO_DEPRECATE
    -Wno-unused-variable
)
target_language_compile_options(electron RC PRIVATE -D_HAS_NODISCARD -D_UNICODE -DUNICODE)
target_language_include_directories(electron ASM_NASM PRIVATE
    ${ELECTRON_SOURCE_DIR}/third_party/ffmpeg/chromium/config/Chrome/win/ia32
    ${ELECTRON_SOURCE_DIR}/third_party/ffmpeg/libavcodec/x86
    ${ELECTRON_SOURCE_DIR}/third_party/ffmpeg/libavutil/x86
    ${ELECTRON_SOURCE_DIR}/third_party/ffmpeg
    ${CMAKE_CURRENT_BINARY_DIR}
)
target_language_include_directories(electron CXX PRIVATE
    ${ELECTRON_SOURCE_DIR}/third_party/skia/include/private
    ${ELECTRON_SOURCE_DIR}/third_party/skia/include/client/android
    ${ELECTRON_SOURCE_DIR}/third_party/skia/src/codec
    ${ELECTRON_SOURCE_DIR}/third_party/skia/src/core
    ${ELECTRON_SOURCE_DIR}/third_party/skia/src/image
    ${ELECTRON_SOURCE_DIR}/third_party/skia/src/images
    ${ELECTRON_SOURCE_DIR}/third_party/skia/src/opts
    ${ELECTRON_SOURCE_DIR}/third_party/skia/src/pdf
    ${ELECTRON_SOURCE_DIR}/third_party/skia/src/ports
    ${ELECTRON_SOURCE_DIR}/third_party/skia/src/shaders
    ${ELECTRON_SOURCE_DIR}/third_party/skia/src/shaders/gradients
    ${ELECTRON_SOURCE_DIR}/third_party/skia/src/sfnt
    ${ELECTRON_SOURCE_DIR}/third_party/skia/src/utils
    ${ELECTRON_SOURCE_DIR}/third_party/skia/src/lazy
    ${ELECTRON_SOURCE_DIR}/third_party/skia/third_party/gif
    ${ELECTRON_SOURCE_DIR}/third_party/skia/src/effects/gradients
    ${ELECTRON_SOURCE_DIR}/third_party/skia/include/utils/win
    ${ELECTRON_SOURCE_DIR}/third_party/skia/src/utils/win
    ${ELECTRON_SOURCE_DIR}/third_party/skia/modules/sksg/include
    ${ELECTRON_SOURCE_DIR}/third_party/skia/modules/skshaper/include
    ${include_dirs_1}
)
target_yasm_sources(electron PRIVATE
    ${ELECTRON_SOURCE_DIR}/third_party/blink/renderer/platform/heap/asm/SaveRegisters_x86.asm
)
set_target_properties(electron PROPERTIES ARCHIVE_OUTPUT_NAME electron.dll)
set_target_properties(electron PROPERTIES VERSION 5.0.5)

add_library(glesv2 SHARED
    ${ELECTRON_SOURCE_DIR}/third_party/angle/src/libGLESv2/entry_points_egl.cpp
    ${ELECTRON_SOURCE_DIR}/third_party/angle/src/libGLESv2/libGLESv2.rc
)
target_link_libraries(glesv2 PRIVATE d3d9 dxguid setupapi)
target_compile_options(glesv2 PRIVATE
    -DLIBGLESV2_IMPLEMENTATION
    -D_HAS_NODISCARD
    -D_UNICODE
    -DUNICODE
    -DANGLE_IS_32_BIT_CPU
    -DGL_APICALL=
    -DGL_API=
    -DGL_GLES_PROTOTYPES=1
    -DEGL_EGL_PROTOTYPES=1
    -DGL_GLEXT_PROTOTYPES
    -DEGL_EGLEXT_PROTOTYPES
    -DANGLE_ENABLE_D3D9
    -DANGLE_ENABLE_D3D11
    -DANGLE_ENABLE_OPENGL
    -DANGLE_ENABLE_OPENGL_NULL
    -DANGLE_ENABLE_VULKAN
    -DANGLE_ENABLE_NULL
    -DLIBANGLE_IMPLEMENTATION
)
target_include_directories(glesv2 PRIVATE
    ${ELECTRON_SOURCE_DIR}/third_party/angle/include
    ${ELECTRON_SOURCE_DIR}/third_party/angle/src
    ${CMAKE_CURRENT_BINARY_DIR}/gen/angle
    ${ELECTRON_SOURCE_DIR}/third_party/angle/src/common/third_party/base
    ${ELECTRON_SOURCE_DIR}/third_party/angle/third_party/vulkan-headers/src/include
)
target_language_compile_options(glesv2 CXX PRIVATE /Oi)
set_target_properties(glesv2 PROPERTIES OUTPUT_NAME libGLESv2)
set_target_properties(glesv2 PROPERTIES ARCHIVE_OUTPUT_NAME libGLESv2.dll)
set_target_properties(glesv2 PROPERTIES VERSION 5.0.5)
