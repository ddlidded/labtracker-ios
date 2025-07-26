import Foundation
import SwiftUI

class DataManager: ObservableObject {
    @Published var columns: [Column] = []
    @Published var methods: [Method] = []
    @Published var analyticsData: AnalyticsData = AnalyticsData()
    
    private let columnsKey = "savedColumns"
    private let methodsKey = "savedMethods"
    
    init() {
        loadData()
        updateAnalytics()
    }
    
    // MARK: - Column Management
    func addColumn(_ column: Column) {
        columns.append(column)
        saveData()
        updateAnalytics()
    }
    
    func updateColumn(_ column: Column) {
        if let index = columns.firstIndex(where: { $0.id == column.id }) {
            columns[index] = column
            saveData()
            updateAnalytics()
        }
    }
    
    func deleteColumn(_ column: Column) {
        columns.removeAll { $0.id == column.id }
        // Remove associated methods
        methods.removeAll { $0.columnId == column.id }
        saveData()
        updateAnalytics()
    }
    
    func getColumn(by id: UUID) -> Column? {
        return columns.first { $0.id == id }
    }
    
    // MARK: - Method Management
    func addMethod(_ method: Method) {
        methods.append(method)
        // Update column method count
        if let columnId = method.columnId {
            updateColumnMethodCount(columnId: columnId)
        }
        saveData()
        updateAnalytics()
    }
    
    func updateMethod(_ method: Method) {
        if let index = methods.firstIndex(where: { $0.id == method.id }) {
            methods[index] = method
            // Update column method count
            if let columnId = method.columnId {
                updateColumnMethodCount(columnId: columnId)
            }
            saveData()
            updateAnalytics()
        }
    }
    
    func deleteMethod(_ method: Method) {
        methods.removeAll { $0.id == method.id }
        // Update column method count
        if let columnId = method.columnId {
            updateColumnMethodCount(columnId: columnId)
        }
        saveData()
        updateAnalytics()
    }
    
    func getMethod(by id: UUID) -> Method? {
        return methods.first { $0.id == id }
    }
    
    func getMethods(for columnId: UUID) -> [Method] {
        return methods.filter { $0.columnId == columnId }
    }
    
    // MARK: - Analytics
    private func updateAnalytics() {
        let totalColumns = columns.count
        let activeColumns = columns.filter { $0.status == .active }.count
        let totalMethods = methods.count
        let activeMethods = methods.filter { $0.status == .active }.count
        
        // Calculate most used column
        let columnUsage = Dictionary(grouping: methods, by: { $0.columnId })
        let mostUsedColumn = columnUsage.max(by: { $0.value.count < $1.value.count })?.key
        let mostUsedColumnName = mostUsedColumn.flatMap { columnId in
            columns.first { $0.id == columnId }?.name
        }
        
        // Calculate average method runtime
        let averageMethodRuntime = methods.isEmpty ? 0.0 : methods.map { $0.runTime }.reduce(0, +) / Double(methods.count)
        
        // Calculate column utilization
        var columnUtilization: [ColumnUtilization] = []
        for column in columns {
            let columnMethods = methods.filter { $0.columnId == column.id }
            let totalRuntime = columnMethods.map { $0.runTime }.reduce(0, +)
            let lastUsed = columnMethods.map { $0.lastModifiedDate }.max()
            
            columnUtilization.append(ColumnUtilization(
                columnName: column.name,
                methodCount: columnMethods.count,
                totalRuntime: totalRuntime,
                lastUsed: lastUsed
            ))
        }
        
        analyticsData = AnalyticsData(
            totalColumns: totalColumns,
            activeColumns: activeColumns,
            totalMethods: totalMethods,
            activeMethods: activeMethods,
            mostUsedColumn: mostUsedColumnName,
            mostUsedMethod: nil, // Could be calculated based on usage frequency
            averageMethodRuntime: averageMethodRuntime,
            columnUtilization: columnUtilization
        )
    }
    
    private func updateColumnMethodCount(columnId: UUID) {
        if let index = columns.firstIndex(where: { $0.id == columnId }) {
            let methodCount = methods.filter { $0.columnId == columnId }.count
            columns[index].methodCount = methodCount
        }
    }
    
    // MARK: - Data Persistence
    private func saveData() {
        if let encodedColumns = try? JSONEncoder().encode(columns) {
            UserDefaults.standard.set(encodedColumns, forKey: columnsKey)
        }
        
        if let encodedMethods = try? JSONEncoder().encode(methods) {
            UserDefaults.standard.set(encodedMethods, forKey: methodsKey)
        }
    }
    
    private func loadData() {
        // Load sample data if no saved data exists
        if UserDefaults.standard.object(forKey: columnsKey) == nil {
            loadSampleData()
        } else {
            if let savedColumns = UserDefaults.standard.data(forKey: columnsKey),
               let decodedColumns = try? JSONDecoder().decode([Column].self, from: savedColumns) {
                columns = decodedColumns
            }
            
            if let savedMethods = UserDefaults.standard.data(forKey: methodsKey),
               let decodedMethods = try? JSONDecoder().decode([Method].self, from: savedMethods) {
                methods = decodedMethods
            }
        }
    }
    
    private func loadSampleData() {
        // Sample columns
        let sampleColumns = [
            Column(
                name: "C18 Column 1",
                type: .reversedPhase,
                dimensions: ColumnDimensions(length: 150, diameter: 4.6),
                particleSize: 5.0,
                poreSize: 100,
                manufacturer: "Waters",
                lotNumber: "LOT123456",
                serialNumber: "SN789012",
                installationDate: Date().addingTimeInterval(-86400 * 30),
                status: .active,
                notes: "Primary reversed phase column for routine analysis"
            ),
            Column(
                name: "HILIC Column",
                type: .hilic,
                dimensions: ColumnDimensions(length: 100, diameter: 2.1),
                particleSize: 3.0,
                poreSize: 130,
                manufacturer: "Agilent",
                lotNumber: "LOT789012",
                serialNumber: "SN345678",
                installationDate: Date().addingTimeInterval(-86400 * 15),
                status: .active,
                notes: "Used for polar compound analysis"
            ),
            Column(
                name: "C8 Column",
                type: .reversedPhase,
                dimensions: ColumnDimensions(length: 250, diameter: 4.6),
                particleSize: 5.0,
                poreSize: 100,
                manufacturer: "Phenomenex",
                lotNumber: "LOT456789",
                serialNumber: "SN901234",
                installationDate: Date().addingTimeInterval(-86400 * 60),
                lastMaintenanceDate: Date().addingTimeInterval(-86400 * 7),
                status: .maintenance,
                notes: "Currently under maintenance"
            )
        ]
        
        // Sample methods
        let sampleMethods = [
            Method(
                name: "Standard C18 Method",
                description: "Standard reversed phase method for routine analysis",
                columnId: sampleColumns[0].id,
                columnName: sampleColumns[0].name,
                flowRate: 1.0,
                temperature: 40.0,
                pressure: 2000.0,
                injectionVolume: 10.0,
                runTime: 15.0,
                mobilePhase: MobilePhase(
                    solventA: "Water + 0.1% Formic Acid",
                    solventB: "Acetonitrile + 0.1% Formic Acid",
                    gradient: .gradient,
                    composition: [
                        GradientStep(time: 0, percentageA: 95, percentageB: 5),
                        GradientStep(time: 10, percentageA: 5, percentageB: 95),
                        GradientStep(time: 15, percentageA: 5, percentageB: 95)
                    ]
                ),
                detection: .uv,
                status: .active,
                notes: "Standard method for pharmaceutical analysis"
            ),
            Method(
                name: "HILIC Method",
                description: "HILIC method for polar compounds",
                columnId: sampleColumns[1].id,
                columnName: sampleColumns[1].name,
                flowRate: 0.3,
                temperature: 35.0,
                pressure: 1500.0,
                injectionVolume: 5.0,
                runTime: 20.0,
                mobilePhase: MobilePhase(
                    solventA: "Acetonitrile + 0.1% Formic Acid",
                    solventB: "Water + 0.1% Formic Acid",
                    gradient: .gradient,
                    composition: [
                        GradientStep(time: 0, percentageA: 95, percentageB: 5),
                        GradientStep(time: 15, percentageA: 50, percentageB: 50),
                        GradientStep(time: 20, percentageA: 50, percentageB: 50)
                    ]
                ),
                detection: .ms,
                status: .active,
                notes: "Method for polar metabolite analysis"
            )
        ]
        
        columns = sampleColumns
        methods = sampleMethods
    }
    
    // MARK: - Search and Filter
    func searchColumns(query: String) -> [Column] {
        if query.isEmpty {
            return columns
        }
        return columns.filter { column in
            column.name.localizedCaseInsensitiveContains(query) ||
            column.manufacturer.localizedCaseInsensitiveContains(query) ||
            column.type.displayName.localizedCaseInsensitiveContains(query)
        }
    }
    
    func searchMethods(query: String) -> [Method] {
        if query.isEmpty {
            return methods
        }
        return methods.filter { method in
            method.name.localizedCaseInsensitiveContains(query) ||
            (method.description?.localizedCaseInsensitiveContains(query) ?? false) ||
            (method.columnName?.localizedCaseInsensitiveContains(query) ?? false)
        }
    }
    
    func filterColumns(by status: ColumnStatus?) -> [Column] {
        guard let status = status else { return columns }
        return columns.filter { $0.status == status }
    }
    
    func filterMethods(by status: MethodStatus?) -> [Method] {
        guard let status = status else { return methods }
        return methods.filter { $0.status == status }
    }
}