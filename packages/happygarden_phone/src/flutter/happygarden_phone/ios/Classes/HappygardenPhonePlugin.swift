import Flutter
import UIKit
import WidgetKit

public class HappygardenPhonePlugin: NSObject, FlutterPlugin {
  public static func register(with registrar: FlutterPluginRegistrar) {
    let channel = FlutterMethodChannel(
      name: "happygarden_phone",
      binaryMessenger: registrar.messenger()
    )
    registrar.addMethodCallDelegate(HappygardenPhonePlugin(), channel: channel)
  }

  public func handle(_ call: FlutterMethodCall, result: @escaping FlutterResult) {
    guard call.method == "publish" else {
      result(FlutterMethodNotImplemented)
      return
    }
    let args = call.arguments as? [String: Any]
    let lines = args?["lines"] as? [String] ?? []
    let text = lines.joined(separator: "\n")
    UserDefaults(suiteName: "group.com.happygarden.app")?.set(text, forKey: "lines")
    if #available(iOS 14.0, *) {
      WidgetCenter.shared.reloadAllTimelines()
    }
    result(true)
  }
}
