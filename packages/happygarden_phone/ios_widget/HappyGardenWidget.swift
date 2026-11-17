import SwiftUI
import WidgetKit

private let appGroup = "group.com.happygarden.app"
private let fallback = "До поливки 1 година"

struct GardenEntry: TimelineEntry {
    let date: Date
    let text: String
}

struct GardenProvider: TimelineProvider {
    func placeholder(in context: Context) -> GardenEntry {
        GardenEntry(date: Date(), text: fallback)
    }

    func getSnapshot(in context: Context, completion: @escaping (GardenEntry) -> Void) {
        completion(GardenEntry(date: Date(), text: load()))
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<GardenEntry>) -> Void) {
        let entry = GardenEntry(date: Date(), text: load())
        let next = Calendar.current.date(byAdding: .minute, value: 30, to: Date()) ?? Date().addingTimeInterval(1800)
        completion(Timeline(entries: [entry], policy: .after(next)))
    }

    func load() -> String {
        let text = UserDefaults(suiteName: appGroup)?.string(forKey: "lines") ?? ""
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        return trimmed.isEmpty ? fallback : trimmed
    }
}

private struct GardenBackground: ViewModifier {
    func body(content: Content) -> some View {
        if #available(iOS 17.0, *) {
            content.containerBackground(Color(red: 0.957, green: 0.969, blue: 0.949), for: .widget)
        } else {
            content.background(Color(red: 0.957, green: 0.969, blue: 0.949))
        }
    }
}

struct GardenWidgetView: View {
    var entry: GardenEntry

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("HappyGarden")
                .font(.caption.weight(.semibold))
                .foregroundColor(Color(red: 0.18, green: 0.49, blue: 0.20))
            Text(entry.text)
                .font(.system(size: 16, weight: .semibold))
                .foregroundColor(Color(red: 0.11, green: 0.18, blue: 0.11))
                .minimumScaleFactor(0.65)
                .lineLimit(6)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .padding(12)
        .modifier(GardenBackground())
    }
}

struct HappyGardenWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "HappyGardenWidget", provider: GardenProvider()) { entry in
            GardenWidgetView(entry: entry)
        }
        .configurationDisplayName("Город")
        .description("До поливки, ріст і стан рослин")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

@main
struct HappyGardenWidgetBundle: WidgetBundle {
    var body: some Widget {
        HappyGardenWidget()
    }
}
