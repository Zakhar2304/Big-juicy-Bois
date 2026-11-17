import 'package:flet/flet.dart';

import 'phone_widget.dart';

class Extension extends FletExtension {
  @override
  FletService? createService(Control control) {
    switch (control.type) {
      case "PhoneWidget":
        return PhoneWidgetControl(control: control);
      default:
        return null;
    }
  }
}
