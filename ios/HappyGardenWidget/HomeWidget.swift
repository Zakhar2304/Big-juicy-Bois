import AppIntents
import SwiftUI
import WidgetKit

private let appGroup = "group.com.happygarden.app"
private let folder = "HappyGardenWidgets"

struct PotItem: Codable, Identifiable {
    var id: String
    var name: String
    var stage: String
    var health: Int
    var glyph: String
    var image: String
    var pinned: Bool
}

struct ShelfFile: Codable {
    var pots: [PotItem]
}

enum WidgetStore {
    static func load() -> [PotItem] {
        guard let base = FileManager.default.containerURL(
            forSecurityApplicationGroupIdentifier: appGroup
        ) else { return [] }
        let url = base.appendingPathComponent("\(folder)/state.json")
        guard let data = try? Data(contentsOf: url),
              let shelf = try? JSONDecoder().decode(ShelfFile.self, from: data) else { return [] }
        return shelf.pots
    }

    static func image(named name: String) -> UIImage? {
        guard !name.isEmpty,
              let base = FileManager.default.containerURL(
                forSecurityApplicationGroupIdentifier: appGroup
              ) else { return nil }
        let url = base.appendingPathComponent("\(folder)/images/\(name)")
        return UIImage(contentsOfFile: url.path)
    }

    static func shelfPots() -> [PotItem] {
        let pots = load()
        let pinned = pots.filter(\.pinned)
        return pinned.isEmpty ? pots : pinned
    }
}

struct PotChoice: AppEntity, Identifiable {
    var id: String
    var name: String

    static var typeDisplayRepresentation = TypeDisplayRepresentation(name: "Горщик")
    static var defaultQuery = PotChoiceQuery()

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(name)")
    }
}

struct PotChoiceQuery: EntityQuery {
    func entities(for identifiers: [PotChoice.ID]) async throws -> [PotChoice] {
        all().filter { identifiers.contains($0.id) }
    }

    func suggestedEntities() async throws -> [PotChoice] {
        all()
    }

    private func all() -> [PotChoice] {
        WidgetStore.load().map { PotChoice(id: $0.id, name: "\($0.name) · \($0.stage)") }
    }
}

struct PickPotIntent: WidgetConfigurationIntent {
    static var title: LocalizedStringResource = "Горщик"
    static var description = IntentDescription("Одна рослина з грядки на робочому столі")

    @Parameter(title: "Рослина")
    var pot: PotChoice?
}

struct PotEntry: TimelineEntry {
    let date: Date
    let pot: PotItem?
}

struct PotProvider: AppIntentTimelineProvider {
    func placeholder(in context: Context) -> PotEntry {
        PotEntry(date: .now, pot: nil)
    }

    func snapshot(for configuration: PickPotIntent, in context: Context) async -> PotEntry {
        PotEntry(date: .now, pot: resolve(configuration))
    }

    func timeline(for configuration: PickPotIntent, in context: Context) async -> Timeline<PotEntry> {
        let entry = PotEntry(date: .now, pot: resolve(configuration))
        return Timeline(entries: [entry], policy: .after(Date().addingTimeInterval(30 * 60)))
    }

    private func resolve(_ configuration: PickPotIntent) -> PotItem? {
        let pots = WidgetStore.load()
        if let id = configuration.pot?.id, let match = pots.first(where: { $0.id == id }) {
            return match
        }
        return pots.first
    }
}

struct ShelfEntry: TimelineEntry {
    let date: Date
    let pots: [PotItem]
}

struct ShelfProvider: TimelineProvider {
    func placeholder(in context: Context) -> ShelfEntry {
        ShelfEntry(date: .now, pots: [])
    }

    func getSnapshot(in context: Context, completion: @escaping (ShelfEntry) -> Void) {
        completion(ShelfEntry(date: .now, pots: WidgetStore.shelfPots()))
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<ShelfEntry>) -> Void) {
        let entry = ShelfEntry(date: .now, pots: WidgetStore.shelfPots())
        completion(Timeline(entries: [entry], policy: .after(Date().addingTimeInterval(30 * 60))))
    }
}

struct PotFace: View {
    let pot: PotItem?
    var compact = false

    var body: some View {
        VStack(spacing: compact ? 2 : 6) {
            if let pot {
                potImage(pot)
                    .frame(maxWidth: compact ? 64 : 140, maxHeight: compact ? 90 : 160)
                Text(pot.name)
                    .font(compact ? .caption.weight(.semibold) : .headline)
                    .lineLimit(1)
                    .foregroundStyle(Color(red: 0.11, green: 0.18, blue: 0.11))
                Text(pot.stage)
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
            } else {
                Text("🌱").font(.largeTitle)
                Text("Посади рослину")
                    .font(.caption)
                    .multilineTextAlignment(.center)
                    .foregroundStyle(.secondary)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    @ViewBuilder
    private func potImage(_ pot: PotItem) -> some View {
        if let ui = WidgetStore.image(named: pot.image) {
            Image(uiImage: ui).resizable().scaledToFit()
        } else {
            Text(pot.glyph.isEmpty ? "🌱" : pot.glyph).font(.largeTitle)
        }
    }
}

struct PotWidgetView: View {
    var entry: PotEntry

    var body: some View {
        PotFace(pot: entry.pot)
            .containerBackground(Color(red: 0.957, green: 0.969, blue: 0.949), for: .widget)
    }
}

struct ShelfWidgetView: View {
    var entry: ShelfEntry

    var body: some View {
        Group {
            if entry.pots.isEmpty {
                PotFace(pot: nil)
            } else {
                HStack(spacing: 8) {
                    ForEach(Array(entry.pots.prefix(4))) { pot in
                        PotFace(pot: pot, compact: true)
                    }
                }
                .padding(.horizontal, 8)
            }
        }
        .containerBackground(Color(red: 0.957, green: 0.969, blue: 0.949), for: .widget)
    }
}

struct PotWidget: Widget {
    var body: some WidgetConfiguration {
        AppIntentConfiguration(kind: "happygarden.pot", intent: PickPotIntent.self, provider: PotProvider()) { entry in
            PotWidgetView(entry: entry)
        }
        .configurationDisplayName("Горщик")
        .description("Одна рослина з грядки")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

struct ShelfWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "happygarden.shelf", provider: ShelfProvider()) { entry in
            ShelfWidgetView(entry: entry)
        }
        .configurationDisplayName("Полиця")
        .description("Кілька горщиків з грядки")
        .supportedFamilies([.systemMedium, .systemLarge])
    }
}

@main
struct HappyGardenWidgets: WidgetBundle {
    var body: some Widget {
        PotWidget()
        ShelfWidget()
    }
}
