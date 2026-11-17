package com.happygarden.phone;

import android.appwidget.AppWidgetManager;
import android.content.ComponentName;
import android.content.Context;

import java.util.List;

import io.flutter.embedding.engine.plugins.FlutterPlugin;
import io.flutter.plugin.common.MethodCall;
import io.flutter.plugin.common.MethodChannel;

public class HappygardenPhonePlugin implements FlutterPlugin, MethodChannel.MethodCallHandler {
    private MethodChannel channel;
    private Context context;

    @Override
    public void onAttachedToEngine(FlutterPlugin.FlutterPluginBinding binding) {
        context = binding.getApplicationContext();
        channel = new MethodChannel(binding.getBinaryMessenger(), "happygarden_phone");
        channel.setMethodCallHandler(this);
    }

    @Override
    public void onMethodCall(MethodCall call, MethodChannel.Result result) {
        if (!"publish".equals(call.method)) {
            result.notImplemented();
            return;
        }
        StringBuilder text = new StringBuilder();
        Object raw = call.argument("lines");
        if (raw instanceof List) {
            for (Object item : (List<?>) raw) {
                if (text.length() > 0) {
                    text.append('\n');
                }
                text.append(String.valueOf(item));
            }
        }
        context.getSharedPreferences(GardenWidgetProvider.PREFS, Context.MODE_PRIVATE)
                .edit()
                .putString(GardenWidgetProvider.KEY, text.toString())
                .apply();
        AppWidgetManager manager = AppWidgetManager.getInstance(context);
        int[] ids = manager.getAppWidgetIds(new ComponentName(context, GardenWidgetProvider.class));
        for (int id : ids) {
            GardenWidgetProvider.update(context, manager, id);
        }
        result.success(true);
    }

    @Override
    public void onDetachedFromEngine(FlutterPlugin.FlutterPluginBinding binding) {
        if (channel != null) {
            channel.setMethodCallHandler(null);
        }
    }
}
