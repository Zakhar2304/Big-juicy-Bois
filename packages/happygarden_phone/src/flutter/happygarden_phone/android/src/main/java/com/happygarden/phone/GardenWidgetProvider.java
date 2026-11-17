package com.happygarden.phone;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.widget.RemoteViews;

public class GardenWidgetProvider extends AppWidgetProvider {
    static final String PREFS = "happygarden_widget";
    static final String KEY = "lines";

    static void update(Context context, AppWidgetManager manager, int id) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        String text = prefs.getString(KEY, "До поливки 1 година");
        if (text == null || text.trim().isEmpty()) {
            text = "До поливки 1 година";
        }
        RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.garden_widget);
        views.setTextViewText(R.id.lines, text);
        Intent launch = context.getPackageManager().getLaunchIntentForPackage(context.getPackageName());
        if (launch != null) {
            PendingIntent pending = PendingIntent.getActivity(
                    context,
                    0,
                    launch,
                    PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
            views.setOnClickPendingIntent(R.id.root, pending);
        }
        manager.updateAppWidget(id, views);
    }

    @Override
    public void onUpdate(Context context, AppWidgetManager manager, int[] ids) {
        for (int id : ids) {
            update(context, manager, id);
        }
    }
}
