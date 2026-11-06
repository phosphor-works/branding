# SPDX-FileCopyrightText: 2026 fuddlesworth
# SPDX-License-Identifier: CC-BY-SA-4.0

# Shipped at the root of every branding release archive, next to the icon
# trees it installs from:
#
#   hicolor/scalable/apps/<name>.svg         for dark themes
#   hicolor/<N>x<N>/apps/<name>.png          16 to 512
#   hicolor-light/...                         the same for light themes
#
# phosphor_install_brand_icons(<app id> <branding name> [<app id> <branding name>...])
#
# Installs branding's <branding name> icon, every size and both themes, under
# the app's ID, so the icon name matches the app's .desktop file and AppStream
# id:
#
#   phosphor_install_brand_icons(org.phosphor_works.PlasmaZones plasmazones)
#
# The destination is ${KDE_INSTALL_ICONDIR}, else ${CMAKE_INSTALL_DATADIR}/icons,
# else share/icons.

set(_PHOSPHOR_BRANDING_ROOT "${CMAKE_CURRENT_LIST_DIR}/..")

function(phosphor_install_brand_icons)
    list(LENGTH ARGN count)
    math(EXPR odd "${count} % 2")
    if(count EQUAL 0 OR odd)
        message(FATAL_ERROR "phosphor_install_brand_icons: give <app id> <branding name> pairs")
    endif()
    if(DEFINED KDE_INSTALL_ICONDIR)
        set(iconDir "${KDE_INSTALL_ICONDIR}")
    elseif(DEFINED CMAKE_INSTALL_DATADIR)
        set(iconDir "${CMAKE_INSTALL_DATADIR}/icons")
    else()
        set(iconDir "share/icons")
    endif()

    set(args ${ARGN})
    while(args)
        list(POP_FRONT args appId name)
        set(found FALSE)
        foreach(theme hicolor hicolor-light)
            file(GLOB sizes LIST_DIRECTORIES true RELATIVE "${_PHOSPHOR_BRANDING_ROOT}/${theme}"
                 "${_PHOSPHOR_BRANDING_ROOT}/${theme}/*")
            foreach(size IN LISTS sizes)
                foreach(ext svg png)
                    set(file "${_PHOSPHOR_BRANDING_ROOT}/${theme}/${size}/apps/${name}.${ext}")
                    if(EXISTS "${file}")
                        install(FILES "${file}" DESTINATION "${iconDir}/${theme}/${size}/apps"
                                RENAME "${appId}.${ext}")
                        set(found TRUE)
                    endif()
                endforeach()
            endforeach()
        endforeach()
        if(NOT found)
            message(FATAL_ERROR "phosphor_install_brand_icons: branding has no icon named ${name}")
        endif()
    endwhile()
endfunction()
