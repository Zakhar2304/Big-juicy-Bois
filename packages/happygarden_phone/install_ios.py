"""Додає віджет iPhone у вже зібраний Flutter-проєкт Flet.

`flet build` переписує Xcode-проєкт із шаблону, тож скрипт можна запустити знову:

    python3 packages/happygarden_phone/install_ios.py

Він копіює Swift-віджет, вписує target у Runner.xcodeproj і лишає виклик
себе в Podfile, щоб `pod install` повторив це сам.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).resolve().parent / "ios_widget"
MARKER = "happygarden-phone-widget"
GROUP = "group.com.happygarden.app"


def _id(n: int) -> str:
    return f"AA10{n:020X}"


APPEX = _id(1)
PLIST = _id(2)
SWIFT = _id(3)
ENTS = _id(4)
GROUP_ID = _id(5)
SWIFT_BUILD = _id(6)
SOURCES_PHASE = _id(7)
FRAMEWORKS = _id(8)
RESOURCES = _id(9)
TARGET = _id(10)
PROXY = _id(11)
DEPENDENCY = _id(12)
EMBED_FILE = _id(13)
EMBED_PHASE = _id(14)
DEBUG = _id(15)
RELEASE = _id(16)
PROFILE = _id(17)
CONFIGS = _id(18)


def main() -> None:
    flutter = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "build" / "flutter"
    ios = flutter / "ios"
    project = ios / "Runner.xcodeproj" / "project.pbxproj"
    if not project.is_file():
        raise SystemExit(f"Немає Xcode-проєкту: {project}")
    _copy_sources(ios)
    _entitlements(ios)
    text = project.read_text(encoding="utf-8")
    if "HappyGardenWidget.appex" not in text:
        text = _patch_project(text)
        project.write_text(text, encoding="utf-8")
    elif "CODE_SIGN_ENTITLEMENTS = Runner/Runner.entitlements;" not in text:
        text = text.replace(
            "INFOPLIST_FILE = Runner/Info.plist;\n",
            "INFOPLIST_FILE = Runner/Info.plist;\n\t\t\t\tCODE_SIGN_ENTITLEMENTS = Runner/Runner.entitlements;\n",
        )
        project.write_text(text, encoding="utf-8")
    _podfile(ios / "Podfile")
    print(f"Віджет iPhone стоїть у {ios / 'HappyGardenWidget'}")


def _copy_sources(ios: Path) -> None:
    folder = ios / "HappyGardenWidget"
    folder.mkdir(parents=True, exist_ok=True)
    for name in ("HappyGardenWidget.swift", "Info.plist", "HappyGardenWidget.entitlements"):
        shutil.copyfile(SOURCES / name, folder / name)
    runner = ios / "Runner"
    runner.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCES / "Runner.entitlements", runner / "Runner.entitlements")


def _entitlements(ios: Path) -> None:
    """Файл уже скопійовано. Тут лише перевірка, що група та сама."""
    text = (ios / "Runner" / "Runner.entitlements").read_text(encoding="utf-8")
    if GROUP not in text:
        raise SystemExit("У Runner.entitlements немає групи віджета")


def _patch_project(text: str) -> str:
    replacements = {
        "/* End PBXBuildFile section */": f"""\t\t{SWIFT_BUILD} /* HappyGardenWidget.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {SWIFT} /* HappyGardenWidget.swift */; }};
\t\t{EMBED_FILE} /* HappyGardenWidget.appex in Embed Foundation Extensions */ = {{isa = PBXBuildFile; fileRef = {APPEX} /* HappyGardenWidget.appex */; settings = {{ATTRIBUTES = (CodeSignOnCopy, RemoveHeadersOnCopy, ); }}; }};
/* End PBXBuildFile section */""",
        "/* End PBXContainerItemProxy section */": f"""\t\t{PROXY} /* PBXContainerItemProxy */ = {{
\t\t\tisa = PBXContainerItemProxy;
\t\t\tcontainerPortal = 97C146E61CF9000F007C117D /* Project object */;
\t\t\tproxyType = 1;
\t\t\tremoteGlobalIDString = {TARGET};
\t\t\tremoteInfo = HappyGardenWidget;
\t\t}};
/* End PBXContainerItemProxy section */""",
        "/* End PBXCopyFilesBuildPhase section */": f"""\t\t{EMBED_PHASE} /* Embed Foundation Extensions */ = {{
\t\t\tisa = PBXCopyFilesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tdstPath = "";
\t\t\tdstSubfolderSpec = 13;
\t\t\tfiles = (
\t\t\t\t{EMBED_FILE} /* HappyGardenWidget.appex in Embed Foundation Extensions */,
\t\t\t);
\t\t\tname = "Embed Foundation Extensions";
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXCopyFilesBuildPhase section */""",
        "/* End PBXFileReference section */": f"""\t\t{APPEX} /* HappyGardenWidget.appex */ = {{isa = PBXFileReference; explicitFileType = "wrapper.app-extension"; includeInIndex = 0; path = HappyGardenWidget.appex; sourceTree = BUILT_PRODUCTS_DIR; }};
\t\t{PLIST} /* Info.plist */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = Info.plist; sourceTree = "<group>"; }};
\t\t{SWIFT} /* HappyGardenWidget.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = HappyGardenWidget.swift; sourceTree = "<group>"; }};
\t\t{ENTS} /* HappyGardenWidget.entitlements */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.entitlements; path = HappyGardenWidget.entitlements; sourceTree = "<group>"; }};
/* End PBXFileReference section */""",
        "/* End PBXFrameworksBuildPhase section */": f"""\t\t{FRAMEWORKS} /* Frameworks */ = {{
\t\t\tisa = PBXFrameworksBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXFrameworksBuildPhase section */""",
        "/* End PBXResourcesBuildPhase section */": f"""\t\t{RESOURCES} /* Resources */ = {{
\t\t\tisa = PBXResourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXResourcesBuildPhase section */""",
        "/* End PBXSourcesBuildPhase section */": f"""\t\t{SOURCES_PHASE} /* Sources */ = {{
\t\t\tisa = PBXSourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t\t{SWIFT_BUILD} /* HappyGardenWidget.swift in Sources */,
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXSourcesBuildPhase section */""",
        "/* End PBXTargetDependency section */": f"""\t\t{DEPENDENCY} /* PBXTargetDependency */ = {{
\t\t\tisa = PBXTargetDependency;
\t\t\ttarget = {TARGET} /* HappyGardenWidget */;
\t\t\ttargetProxy = {PROXY} /* PBXContainerItemProxy */;
\t\t}};
/* End PBXTargetDependency section */""",
        "/* End PBXNativeTarget section */": f"""\t\t{TARGET} /* HappyGardenWidget */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = {CONFIGS} /* Build configuration list for PBXNativeTarget "HappyGardenWidget" */;
\t\t\tbuildPhases = (
\t\t\t\t{SOURCES_PHASE} /* Sources */,
\t\t\t\t{FRAMEWORKS} /* Frameworks */,
\t\t\t\t{RESOURCES} /* Resources */,
\t\t\t);
\t\t\tbuildRules = (
\t\t\t);
\t\t\tdependencies = (
\t\t\t);
\t\t\tname = HappyGardenWidget;
\t\t\tproductName = HappyGardenWidget;
\t\t\tproductReference = {APPEX} /* HappyGardenWidget.appex */;
\t\t\tproductType = "com.apple.product-type.app-extension";
\t\t}};
/* End PBXNativeTarget section */""",
        "/* End XCBuildConfiguration section */": _configs() + "\n/* End XCBuildConfiguration section */",
        "/* End XCConfigurationList section */": f"""\t\t{CONFIGS} /* Build configuration list for PBXNativeTarget "HappyGardenWidget" */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{DEBUG} /* Debug */,
\t\t\t\t{RELEASE} /* Release */,
\t\t\t\t{PROFILE} /* Profile */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};
/* End XCConfigurationList section */""",
    }
    for needle, block in replacements.items():
        if needle not in text:
            raise SystemExit(f"У проєкті Xcode немає {needle}")
        text = text.replace(needle, block, 1)

    text = text.replace(
        "\t\t\t\t97C146F01CF9000F007C117D /* Runner */,\n",
        "\t\t\t\t97C146F01CF9000F007C117D /* Runner */,\n\t\t\t\t"
        + GROUP_ID
        + " /* HappyGardenWidget */,\n",
        1,
    )
    group = f"""\t\t{GROUP_ID} /* HappyGardenWidget */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{SWIFT} /* HappyGardenWidget.swift */,
\t\t\t\t{PLIST} /* Info.plist */,
\t\t\t\t{ENTS} /* HappyGardenWidget.entitlements */,
\t\t\t);
\t\t\tpath = HappyGardenWidget;
\t\t\tsourceTree = "<group>";
\t\t}};
/* End PBXGroup section */"""
    text = text.replace("/* End PBXGroup section */", group, 1)
    text = text.replace(
        "\t\t\t\t331C8081294A63A400263BE5 /* RunnerTests.xctest */,\n",
        "\t\t\t\t331C8081294A63A400263BE5 /* RunnerTests.xctest */,\n\t\t\t\t"
        + APPEX
        + " /* HappyGardenWidget.appex */,\n",
        1,
    )
    text = text.replace(
        "\t\t\t\t9705A1C41CF9048500538489 /* Embed Frameworks */,\n",
        "\t\t\t\t9705A1C41CF9048500538489 /* Embed Frameworks */,\n\t\t\t\t"
        + EMBED_PHASE
        + " /* Embed Foundation Extensions */,\n",
        1,
    )
    text = text.replace(
        "\t\t\tdependencies = (\n\t\t\t);\n\t\t\tname = Runner;\n",
        "\t\t\tdependencies = (\n\t\t\t\t"
        + DEPENDENCY
        + " /* PBXTargetDependency */,\n\t\t\t);\n\t\t\tname = Runner;\n",
        1,
    )
    text = text.replace(
        "\t\t\t\t331C8080294A63A400263BE5 /* RunnerTests */,\n",
        "\t\t\t\t331C8080294A63A400263BE5 /* RunnerTests */,\n\t\t\t\t"
        + TARGET
        + " /* HappyGardenWidget */,\n",
        1,
    )
    text = text.replace(
        "\t\t\t\t\t97C146ED1CF9000F007C117D = {\n\t\t\t\t\t\tCreatedOnToolsVersion = 7.3.1;\n\t\t\t\t\t\tLastSwiftMigration = 1100;\n\t\t\t\t\t};",
        "\t\t\t\t\t97C146ED1CF9000F007C117D = {\n\t\t\t\t\t\tCreatedOnToolsVersion = 7.3.1;\n\t\t\t\t\t\tLastSwiftMigration = 1100;\n\t\t\t\t\t};\n\t\t\t\t\t"
        + TARGET
        + " = {\n\t\t\t\t\t\tCreatedOnToolsVersion = 15.0;\n\t\t\t\t\t};",
        1,
    )
    if "CODE_SIGN_ENTITLEMENTS = Runner/Runner.entitlements;" not in text:
        text = text.replace(
            "INFOPLIST_FILE = Runner/Info.plist;\n",
            "INFOPLIST_FILE = Runner/Info.plist;\n\t\t\t\tCODE_SIGN_ENTITLEMENTS = Runner/Runner.entitlements;\n",
        )
    return text


def _configs() -> str:
    common = """\t\t\tAPPLICATION_EXTENSION_API_ONLY = YES;
\t\t\tCODE_SIGN_ENTITLEMENTS = HappyGardenWidget/HappyGardenWidget.entitlements;
\t\t\tCODE_SIGN_STYLE = Manual;
\t\t\tCURRENT_PROJECT_VERSION = 1;
\t\t\tGENERATE_INFOPLIST_FILE = NO;
\t\t\tINFOPLIST_FILE = HappyGardenWidget/Info.plist;
\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 15.0;
\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t"$(inherited)",
\t\t\t\t"@executable_path/Frameworks",
\t\t\t\t"@executable_path/../../Frameworks",
\t\t\t);
\t\t\tMARKETING_VERSION = 1.0;
\t\t\tPRODUCT_BUNDLE_IDENTIFIER = com.happygarden.app.widget;
\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\tSKIP_INSTALL = YES;
\t\t\tSWIFT_VERSION = 5.0;
\t\t\tTARGETED_DEVICE_FAMILY = "1,2";"""
    debug_extra = """\t\t\tSWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG;
\t\t\tSWIFT_OPTIMIZATION_LEVEL = "-Onone";"""
    chunks = []
    for ident, name, extra in (
        (DEBUG, "Debug", debug_extra + "\n" + common),
        (RELEASE, "Release", common),
        (PROFILE, "Profile", common),
    ):
        chunks.append(
            f"""\t\t{ident} /* {name} */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
{extra}
\t\t\t}};
\t\t\tname = {name};
\t\t}};"""
        )
    return "\n".join(chunks)


def _podfile(path: Path) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return
    hook = f"""
  # {MARKER}
  widget = File.expand_path('../../../packages/happygarden_phone/install_ios.py', __dir__)
  if File.exist?(widget)
    system('python3', widget)
  end
"""
    if not text.endswith("\n"):
        text += "\n"
    head, sep, _tail = text.rpartition("\nend\n")
    if not sep:
        return
    path.write_text(head + "\n" + hook + "end\n", encoding="utf-8")


if __name__ == "__main__":
    main()
