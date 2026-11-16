#!/usr/bin/env python3
"""Додає WidgetKit-розширення в згенерований Flet iOS-проєкт.

Flet перезаписує build/flutter/ios, тому скрипт запускають після `flet build`.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

MARKER = "A11CE0000000000000000A0B"
GROUP = "group.com.happygarden.app"

ENTITLEMENTS = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>com.apple.security.application-groups</key>
	<array>
		<string>{GROUP}</string>
	</array>
</dict>
</plist>
"""

SYNC_SWIFT = f"""
  func syncHappyGardenWidgets() {{
    let fm = FileManager.default
    guard let docs = fm.urls(for: .documentDirectory, in: .userDomainMask).first,
          let group = fm.containerURL(forSecurityApplicationGroupIdentifier: "{GROUP}") else {{ return }}
    let src = docs.appendingPathComponent("HappyGardenWidgets", isDirectory: true)
    guard fm.fileExists(atPath: src.path) else {{ return }}
    let dst = group.appendingPathComponent("HappyGardenWidgets", isDirectory: true)
    if fm.fileExists(atPath: dst.path) {{ try? fm.removeItem(at: dst) }}
    try? fm.copyItem(at: src, to: dst)
    WidgetCenter.shared.reloadAllTimelines()
  }}

  override func applicationWillResignActive(_ application: UIApplication) {{
    syncHappyGardenWidgets()
    super.applicationWillResignActive(application)
  }}
"""


def team_id(pbx: str) -> str:
    needle = "DEVELOPMENT_TEAM = "
    start = pbx.find(needle)
    if start < 0:
        return "R7NKNUH88G"
    rest = pbx[start + len(needle) :]
    return rest.split(";", 1)[0].strip() or "R7NKNUH88G"


def patch_delegate(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "import WidgetKit" not in text:
        text = text.replace("import UIKit\n", "import UIKit\nimport WidgetKit\n", 1)
    if "syncHappyGardenWidgets()" not in text.split("func syncHappyGardenWidgets", 1)[0]:
        old = "    return super.application(application, didFinishLaunchingWithOptions: launchOptions)\n"
        new = "    syncHappyGardenWidgets()\n" + old
        if old not in text:
            raise SystemExit(f"Не знайшов точку запуску в {path}")
        text = text.replace(old, new, 1)
    if "func syncHappyGardenWidgets()" not in text:
        close = text.rfind("\n}")
        text = text[:close] + "\n" + SYNC_SWIFT + text[close:]
    path.write_text(text, encoding="utf-8")


def patch_project(path: Path, team: str) -> None:
    text = path.read_text(encoding="utf-8")
    if "CODE_SIGN_ENTITLEMENTS = Runner/Runner.entitlements;" not in text:
        text = text.replace(
            "INFOPLIST_FILE = Runner/Info.plist;\n",
            "CODE_SIGN_ENTITLEMENTS = Runner/Runner.entitlements;\n"
            "\t\t\t\tINFOPLIST_FILE = Runner/Info.plist;\n",
        )
    # Цей прапорець змушує підпис узяти лише файл entitlements і викинути
    # application-identifier. Без нього iPhone не встановлює debug-збірку.
    text = text.replace("\t\t\t\tCODE_SIGN_ALLOW_ENTITLEMENTS_MODIFICATION = YES;\n", "")
    if MARKER in text:
        path.write_text(text, encoding="utf-8")
        return

    block = f"""
/* Begin HappyGarden widget */
		A11CE0000000000000000A05 /* HomeWidget.swift in Sources */ = {{isa = PBXBuildFile; fileRef = A11CE0000000000000000A01 /* HomeWidget.swift */; }};
		A11CE0000000000000000A06 /* HappyGardenWidget.appex in Embed Foundation Extensions */ = {{isa = PBXBuildFile; fileRef = A11CE0000000000000000A04 /* HappyGardenWidget.appex */; settings = {{ATTRIBUTES = (RemoveHeadersOnCopy, ); }}; }};
		A11CE0000000000000000A01 /* HomeWidget.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = HomeWidget.swift; sourceTree = "<group>"; }};
		A11CE0000000000000000A02 /* Info.plist */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = Info.plist; sourceTree = "<group>"; }};
		A11CE0000000000000000A03 /* HappyGardenWidget.entitlements */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.entitlements; path = HappyGardenWidget.entitlements; sourceTree = "<group>"; }};
		A11CE0000000000000000A04 /* HappyGardenWidget.appex */ = {{isa = PBXFileReference; explicitFileType = "wrapper.app-extension"; includeInIndex = 0; path = HappyGardenWidget.appex; sourceTree = BUILT_PRODUCTS_DIR; }};
/* End HappyGarden widget files */
"""
    text = text.replace("/* End PBXBuildFile section */", block + "/* End PBXBuildFile section */", 1)

    text = text.replace(
        "97C146EE1CF9000F007C117D /* happygarden.app */,\n",
        "97C146EE1CF9000F007C117D /* happygarden.app */,\n"
        "\t\t\t\tA11CE0000000000000000A04 /* HappyGardenWidget.appex */,\n",
        1,
    )
    text = text.replace(
        "331C8082294A63A400263BE5 /* RunnerTests */,\n",
        "331C8082294A63A400263BE5 /* RunnerTests */,\n"
        "\t\t\t\tA11CE0000000000000000A07 /* HappyGardenWidget */,\n",
        1,
    )
    group = """
		A11CE0000000000000000A07 /* HappyGardenWidget */ = {
			isa = PBXGroup;
			children = (
				A11CE0000000000000000A01 /* HomeWidget.swift */,
				A11CE0000000000000000A02 /* Info.plist */,
				A11CE0000000000000000A03 /* HappyGardenWidget.entitlements */,
			);
			path = HappyGardenWidget;
			sourceTree = "<group>";
		};
"""
    text = text.replace("/* End PBXGroup section */", group + "/* End PBXGroup section */", 1)

    target = f"""
		{MARKER} /* HappyGardenWidget */ = {{
			isa = PBXNativeTarget;
			buildConfigurationList = A11CE0000000000000000A0F /* Build configuration list for PBXNativeTarget "HappyGardenWidget" */;
			buildPhases = (
				A11CE0000000000000000A08 /* Sources */,
				A11CE0000000000000000A09 /* Resources */,
				A11CE0000000000000000A0A /* Frameworks */,
			);
			buildRules = (
			);
			dependencies = (
			);
			name = HappyGardenWidget;
			productName = HappyGardenWidget;
			productReference = A11CE0000000000000000A04 /* HappyGardenWidget.appex */;
			productType = "com.apple.product-type.app-extension";
		}};
"""
    text = text.replace("/* End PBXNativeTarget section */", target + "/* End PBXNativeTarget section */", 1)
    text = text.replace(
        "97C146ED1CF9000F007C117D /* Runner */,\n",
        "97C146ED1CF9000F007C117D /* Runner */,\n"
        f"\t\t\t\t{MARKER} /* HappyGardenWidget */,\n",
        1,
    )
    text = text.replace(
        """				9705A1C41CF9048500538489 /* Embed Frameworks */,
""",
        """				9705A1C41CF9048500538489 /* Embed Frameworks */,
				A11CE0000000000000000A0C /* Embed Foundation Extensions */,
""",
        1,
    )
    text = text.replace(
        """			dependencies = (
			);
			name = Runner;
""",
        """			dependencies = (
				A11CE0000000000000000A0E /* PBXTargetDependency */,
			);
			name = Runner;
""",
        1,
    )
    phases = """
		A11CE0000000000000000A08 /* Sources */ = {
			isa = PBXSourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
				A11CE0000000000000000A05 /* HomeWidget.swift in Sources */,
			);
			runOnlyForDeploymentPostprocessing = 0;
		};
		A11CE0000000000000000A09 /* Resources */ = {
			isa = PBXResourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
			);
			runOnlyForDeploymentPostprocessing = 0;
		};
		A11CE0000000000000000A0A /* Frameworks */ = {
			isa = PBXFrameworksBuildPhase;
			buildActionMask = 2147483647;
			files = (
			);
			runOnlyForDeploymentPostprocessing = 0;
		};
		A11CE0000000000000000A0C /* Embed Foundation Extensions */ = {
			isa = PBXCopyFilesBuildPhase;
			buildActionMask = 2147483647;
			dstPath = "";
			dstSubfolderSpec = 13;
			files = (
				A11CE0000000000000000A06 /* HappyGardenWidget.appex in Embed Foundation Extensions */,
			);
			name = "Embed Foundation Extensions";
			runOnlyForDeploymentPostprocessing = 0;
		};
		A11CE0000000000000000A0D /* PBXContainerItemProxy */ = {
			isa = PBXContainerItemProxy;
			containerPortal = 97C146E61CF9000F007C117D /* Project object */;
			proxyType = 1;
			remoteGlobalIDString = A11CE0000000000000000A0B;
			remoteInfo = HappyGardenWidget;
		};
		A11CE0000000000000000A0E /* PBXTargetDependency */ = {
			isa = PBXTargetDependency;
			target = A11CE0000000000000000A0B /* HappyGardenWidget */;
			targetProxy = A11CE0000000000000000A0D /* PBXContainerItemProxy */;
		};
"""
    text = text.replace("/* End PBXSourcesBuildPhase section */", phases + "/* End PBXSourcesBuildPhase section */", 1)

    configs = f"""
		A11CE0000000000000000A11 /* Debug */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
				APPLICATION_EXTENSION_API_ONLY = YES;
				CODE_SIGN_ENTITLEMENTS = HappyGardenWidget/HappyGardenWidget.entitlements;
				CODE_SIGN_STYLE = Automatic;
				CURRENT_PROJECT_VERSION = 1;
				DEVELOPMENT_TEAM = {team};
				GENERATE_INFOPLIST_FILE = NO;
				INFOPLIST_FILE = HappyGardenWidget/Info.plist;
				IPHONEOS_DEPLOYMENT_TARGET = 17.0;
				LD_RUNPATH_SEARCH_PATHS = (
					"$(inherited)",
					"@executable_path/Frameworks",
					"@executable_path/../../Frameworks",
				);
				MARKETING_VERSION = 0.1.0;
				PRODUCT_BUNDLE_IDENTIFIER = com.happygarden.app.widget;
				PRODUCT_BUNDLE_PACKAGE_TYPE = "XPC!";
				PRODUCT_NAME = "$(TARGET_NAME)";
				SKIP_INSTALL = YES;
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_VERSION = 5.0;
				TARGETED_DEVICE_FAMILY = "1,2";
			}};
			name = Debug;
		}};
		A11CE0000000000000000A12 /* Release */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
				APPLICATION_EXTENSION_API_ONLY = YES;
				CODE_SIGN_ENTITLEMENTS = HappyGardenWidget/HappyGardenWidget.entitlements;
				CODE_SIGN_STYLE = Automatic;
				CURRENT_PROJECT_VERSION = 1;
				DEVELOPMENT_TEAM = {team};
				GENERATE_INFOPLIST_FILE = NO;
				INFOPLIST_FILE = HappyGardenWidget/Info.plist;
				IPHONEOS_DEPLOYMENT_TARGET = 17.0;
				LD_RUNPATH_SEARCH_PATHS = (
					"$(inherited)",
					"@executable_path/Frameworks",
					"@executable_path/../../Frameworks",
				);
				MARKETING_VERSION = 0.1.0;
				PRODUCT_BUNDLE_IDENTIFIER = com.happygarden.app.widget;
				PRODUCT_BUNDLE_PACKAGE_TYPE = "XPC!";
				PRODUCT_NAME = "$(TARGET_NAME)";
				SKIP_INSTALL = YES;
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_VERSION = 5.0;
				TARGETED_DEVICE_FAMILY = "1,2";
			}};
			name = Release;
		}};
		A11CE0000000000000000A13 /* Profile */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
				APPLICATION_EXTENSION_API_ONLY = YES;
				CODE_SIGN_ENTITLEMENTS = HappyGardenWidget/HappyGardenWidget.entitlements;
				CODE_SIGN_STYLE = Automatic;
				CURRENT_PROJECT_VERSION = 1;
				DEVELOPMENT_TEAM = {team};
				GENERATE_INFOPLIST_FILE = NO;
				INFOPLIST_FILE = HappyGardenWidget/Info.plist;
				IPHONEOS_DEPLOYMENT_TARGET = 17.0;
				LD_RUNPATH_SEARCH_PATHS = (
					"$(inherited)",
					"@executable_path/Frameworks",
					"@executable_path/../../Frameworks",
				);
				MARKETING_VERSION = 0.1.0;
				PRODUCT_BUNDLE_IDENTIFIER = com.happygarden.app.widget;
				PRODUCT_BUNDLE_PACKAGE_TYPE = "XPC!";
				PRODUCT_NAME = "$(TARGET_NAME)";
				SKIP_INSTALL = YES;
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_VERSION = 5.0;
				TARGETED_DEVICE_FAMILY = "1,2";
			}};
			name = Profile;
		}};
		A11CE0000000000000000A0F /* Build configuration list for PBXNativeTarget "HappyGardenWidget" */ = {{
			isa = XCConfigurationList;
			buildConfigurations = (
				A11CE0000000000000000A11 /* Debug */,
				A11CE0000000000000000A12 /* Release */,
				A11CE0000000000000000A13 /* Profile */,
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		}};
"""
    text = text.replace("/* End XCConfigurationList section */", configs + "/* End XCConfigurationList section */", 1)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Використання: attach_ios_widget.py <ios-директорія>")
    ios = Path(sys.argv[1]).resolve()
    src = Path(__file__).resolve().parent.parent / "ios" / "HappyGardenWidget"
    dest = ios / "HappyGardenWidget"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    (ios / "Runner" / "Runner.entitlements").write_text(ENTITLEMENTS, encoding="utf-8")
    project = ios / "Runner.xcodeproj" / "project.pbxproj"
    pbx = project.read_text(encoding="utf-8")
    patch_project(project, team_id(pbx))
    patch_delegate(ios / "Runner" / "AppDelegate.swift")
    print(f"Віджет додано: {dest}")


if __name__ == "__main__":
    main()
