import 'package:flet/flet.dart';
import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';

class PhoneWidgetControl extends FletService {
  static const _channel = MethodChannel("happygarden_phone");

  PhoneWidgetControl({required super.control});

  @override
  void init() {
    super.init();
    control.addInvokeMethodListener(_invokeMethod);
  }

  Future<dynamic> _invokeMethod(String name, dynamic args) async {
    if (name != "publish") {
      throw Exception("Unknown PhoneWidget method: $name");
    }
    final raw = args is Map ? args["lines"] : null;
    final lines = raw is List ? raw.map((item) => item.toString()).toList() : <String>[];
    try {
      await _channel.invokeMethod("publish", {"lines": lines});
    } on MissingPluginException {
      return false;
    }
    return true;
  }

  @override
  void dispose() {
    control.removeInvokeMethodListener(_invokeMethod);
    super.dispose();
  }
}
