import Foundation

// MARK: - Column Model
struct Column: Identifiable, Codable {
    let id: UUID
    var name: String
    var type: ColumnType
    var dimensions: ColumnDimensions
    var particleSize: Double
    var poreSize: Double?
    var manufacturer: String
    var lotNumber: String?
    var serialNumber: String?
    var installationDate: Date
    var lastMaintenanceDate: Date?
    var status: ColumnStatus
    var notes: String?
    var methodCount: Int
    
    init(id: UUID = UUID(), name: String, type: ColumnType, dimensions: ColumnDimensions, particleSize: Double, poreSize: Double? = nil, manufacturer: String, lotNumber: String? = nil, serialNumber: String? = nil, installationDate: Date = Date(), lastMaintenanceDate: Date? = nil, status: ColumnStatus = .active, notes: String? = nil, methodCount: Int = 0) {
        self.id = id
        self.name = name
        self.type = type
        self.dimensions = dimensions
        self.particleSize = particleSize
        self.poreSize = poreSize
        self.manufacturer = manufacturer
        self.lotNumber = lotNumber
        self.serialNumber = serialNumber
        self.installationDate = installationDate
        self.lastMaintenanceDate = lastMaintenanceDate
        self.status = status
        self.notes = notes
        self.methodCount = methodCount
    }
}

enum ColumnType: String, CaseIterable, Codable {
    case reversedPhase = "Reversed Phase"
    case normalPhase = "Normal Phase"
    case ionExchange = "Ion Exchange"
    case sizeExclusion = "Size Exclusion"
    case affinity = "Affinity"
    case chiral = "Chiral"
    case hilic = "HILIC"
    case other = "Other"
    
    var displayName: String {
        return self.rawValue
    }
}

struct ColumnDimensions: Codable {
    let length: Double
    let diameter: Double
    
    var volume: Double {
        return Double.pi * pow(diameter / 2, 2) * length
    }
    
    var displayString: String {
        return "\(length) × \(diameter) mm"
    }
}

enum ColumnStatus: String, CaseIterable, Codable {
    case active = "Active"
    case maintenance = "Maintenance"
    case retired = "Retired"
    case damaged = "Damaged"
    
    var color: String {
        switch self {
        case .active:
            return "green"
        case .maintenance:
            return "orange"
        case .retired:
            return "gray"
        case .damaged:
            return "red"
        }
    }
}

// MARK: - Method Model
struct Method: Identifiable, Codable {
    let id: UUID
    var name: String
    var description: String?
    var columnId: UUID?
    var columnName: String?
    var flowRate: Double
    var temperature: Double?
    var pressure: Double?
    var injectionVolume: Double
    var runTime: Double
    var mobilePhase: MobilePhase
    var detection: DetectionType
    var createdDate: Date
    var lastModifiedDate: Date
    var status: MethodStatus
    var notes: String?
    
    init(id: UUID = UUID(), name: String, description: String? = nil, columnId: UUID? = nil, columnName: String? = nil, flowRate: Double, temperature: Double? = nil, pressure: Double? = nil, injectionVolume: Double, runTime: Double, mobilePhase: MobilePhase, detection: DetectionType, createdDate: Date = Date(), lastModifiedDate: Date = Date(), status: MethodStatus = .active, notes: String? = nil) {
        self.id = id
        self.name = name
        self.description = description
        self.columnId = columnId
        self.columnName = columnName
        self.flowRate = flowRate
        self.temperature = temperature
        self.pressure = pressure
        self.injectionVolume = injectionVolume
        self.runTime = runTime
        self.mobilePhase = mobilePhase
        self.detection = detection
        self.createdDate = createdDate
        self.lastModifiedDate = lastModifiedDate
        self.status = status
        self.notes = notes
    }
}

struct MobilePhase: Codable {
    var solventA: String
    var solventB: String
    var gradient: GradientType
    var composition: [GradientStep]
    
    init(solventA: String, solventB: String, gradient: GradientType = .isocratic, composition: [GradientStep] = []) {
        self.solventA = solventA
        self.solventB = solventB
        self.gradient = gradient
        self.composition = composition
    }
}

enum GradientType: String, CaseIterable, Codable {
    case isocratic = "Isocratic"
    case gradient = "Gradient"
    case step = "Step"
}

struct GradientStep: Codable, Identifiable {
    let id = UUID()
    var time: Double
    var percentageA: Double
    var percentageB: Double
    
    init(time: Double, percentageA: Double, percentageB: Double) {
        self.time = time
        self.percentageA = percentageA
        self.percentageB = percentageB
    }
}

enum DetectionType: String, CaseIterable, Codable {
    case uv = "UV"
    case ms = "MS"
    case fluorescence = "Fluorescence"
    case refractiveIndex = "Refractive Index"
    case conductivity = "Conductivity"
    case electrochemical = "Electrochemical"
    case other = "Other"
}

enum MethodStatus: String, CaseIterable, Codable {
    case active = "Active"
    case draft = "Draft"
    case archived = "Archived"
    case validation = "Validation"
    
    var color: String {
        switch self {
        case .active:
            return "green"
        case .draft:
            return "blue"
        case .archived:
            return "gray"
        case .validation:
            return "orange"
        }
    }
}

// MARK: - Analytics Data
struct AnalyticsData: Codable {
    var totalColumns: Int
    var activeColumns: Int
    var totalMethods: Int
    var activeMethods: Int
    var mostUsedColumn: String?
    var mostUsedMethod: String?
    var averageMethodRuntime: Double
    var columnUtilization: [ColumnUtilization]
    
    init(totalColumns: Int = 0, activeColumns: Int = 0, totalMethods: Int = 0, activeMethods: Int = 0, mostUsedColumn: String? = nil, mostUsedMethod: String? = nil, averageMethodRuntime: Double = 0.0, columnUtilization: [ColumnUtilization] = []) {
        self.totalColumns = totalColumns
        self.activeColumns = activeColumns
        self.totalMethods = totalMethods
        self.activeMethods = activeMethods
        self.mostUsedColumn = mostUsedColumn
        self.mostUsedMethod = mostUsedMethod
        self.averageMethodRuntime = averageMethodRuntime
        self.columnUtilization = columnUtilization
    }
}

struct ColumnUtilization: Codable, Identifiable {
    let id = UUID()
    var columnName: String
    var methodCount: Int
    var totalRuntime: Double
    var lastUsed: Date?
    
    init(columnName: String, methodCount: Int, totalRuntime: Double, lastUsed: Date? = nil) {
        self.columnName = columnName
        self.methodCount = methodCount
        self.totalRuntime = totalRuntime
        self.lastUsed = lastUsed
    }
}