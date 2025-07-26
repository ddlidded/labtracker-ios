import SwiftUI

struct ContentView: View {
    @StateObject private var dataManager = DataManager()
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            DashboardView()
                .environmentObject(dataManager)
                .tabItem {
                    Image(systemName: "chart.bar.fill")
                    Text("Dashboard")
                }
                .tag(0)
            
            ColumnListView()
                .environmentObject(dataManager)
                .tabItem {
                    Image(systemName: "cylinder.fill")
                    Text("Columns")
                }
                .tag(1)
            
            MethodListView()
                .environmentObject(dataManager)
                .tabItem {
                    Image(systemName: "list.bullet")
                    Text("Methods")
                }
                .tag(2)
            
            AnalyticsView()
                .environmentObject(dataManager)
                .tabItem {
                    Image(systemName: "chart.line.uptrend.xyaxis")
                    Text("Analytics")
                }
                .tag(3)
        }
        .accentColor(.blue)
    }
}

struct DashboardView: View {
    @EnvironmentObject var dataManager: DataManager
    
    var body: some View {
        NavigationView {
            ScrollView {
                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible())
                ], spacing: 16) {
                    // Summary Cards
                    SummaryCard(
                        title: "Total Columns",
                        value: "\(dataManager.analyticsData.totalColumns)",
                        icon: "cylinder.fill",
                        color: .blue
                    )
                    
                    SummaryCard(
                        title: "Active Columns",
                        value: "\(dataManager.analyticsData.activeColumns)",
                        icon: "checkmark.circle.fill",
                        color: .green
                    )
                    
                    SummaryCard(
                        title: "Total Methods",
                        value: "\(dataManager.analyticsData.totalMethods)",
                        icon: "list.bullet",
                        color: .orange
                    )
                    
                    SummaryCard(
                        title: "Active Methods",
                        value: "\(dataManager.analyticsData.activeMethods)",
                        icon: "play.circle.fill",
                        color: .purple
                    )
                }
                .padding()
                
                // Recent Activity
                VStack(alignment: .leading, spacing: 16) {
                    Text("Recent Activity")
                        .font(.title2)
                        .fontWeight(.bold)
                        .padding(.horizontal)
                    
                    RecentActivityView()
                        .environmentObject(dataManager)
                }
                
                // Quick Actions
                VStack(alignment: .leading, spacing: 16) {
                    Text("Quick Actions")
                        .font(.title2)
                        .fontWeight(.bold)
                        .padding(.horizontal)
                    
                    QuickActionsView()
                        .environmentObject(dataManager)
                }
            }
            .navigationTitle("Kapelczak MS Visualizer")
            .navigationBarTitleDisplayMode(.large)
        }
    }
}

struct SummaryCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: icon)
                .font(.title)
                .foregroundColor(color)
            
            Text(value)
                .font(.title2)
                .fontWeight(.bold)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.1), radius: 4, x: 0, y: 2)
    }
}

struct RecentActivityView: View {
    @EnvironmentObject var dataManager: DataManager
    
    var body: some View {
        VStack(spacing: 0) {
            ForEach(Array(dataManager.methods.prefix(5)), id: \.id) { method in
                HStack {
                    Image(systemName: "clock")
                        .foregroundColor(.blue)
                        .frame(width: 20)
                    
                    VStack(alignment: .leading, spacing: 2) {
                        Text(method.name)
                            .font(.subheadline)
                            .fontWeight(.medium)
                        
                        Text("Modified \(method.lastModifiedDate, style: .relative) ago")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    
                    Spacer()
                    
                    Text(method.status.rawValue)
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color(method.status.color).opacity(0.2))
                        .foregroundColor(Color(method.status.color))
                        .cornerRadius(8)
                }
                .padding(.horizontal)
                .padding(.vertical, 8)
                
                if method.id != dataManager.methods.prefix(5).last?.id {
                    Divider()
                        .padding(.leading, 44)
                }
            }
        }
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.1), radius: 4, x: 0, y: 2)
        .padding(.horizontal)
    }
}

struct QuickActionsView: View {
    @EnvironmentObject var dataManager: DataManager
    @State private var showingAddColumn = false
    @State private var showingAddMethod = false
    
    var body: some View {
        HStack(spacing: 16) {
            Button(action: {
                showingAddColumn = true
            }) {
                VStack(spacing: 8) {
                    Image(systemName: "plus.circle.fill")
                        .font(.title)
                        .foregroundColor(.blue)
                    
                    Text("Add Column")
                        .font(.caption)
                        .fontWeight(.medium)
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color(.systemBackground))
                .cornerRadius(12)
                .shadow(color: .black.opacity(0.1), radius: 4, x: 0, y: 2)
            }
            
            Button(action: {
                showingAddMethod = true
            }) {
                VStack(spacing: 8) {
                    Image(systemName: "plus.circle.fill")
                        .font(.title)
                        .foregroundColor(.orange)
                    
                    Text("Add Method")
                        .font(.caption)
                        .fontWeight(.medium)
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color(.systemBackground))
                .cornerRadius(12)
                .shadow(color: .black.opacity(0.1), radius: 4, x: 0, y: 2)
            }
        }
        .padding(.horizontal)
        .sheet(isPresented: $showingAddColumn) {
            AddColumnView()
                .environmentObject(dataManager)
        }
        .sheet(isPresented: $showingAddMethod) {
            AddMethodView()
                .environmentObject(dataManager)
        }
    }
}

struct AddColumnView: View {
    @EnvironmentObject var dataManager: DataManager
    @Environment(\.presentationMode) var presentationMode
    
    @State private var name = ""
    @State private var type = ColumnType.reversedPhase
    @State private var length = ""
    @State private var diameter = ""
    @State private var particleSize = ""
    @State private var poreSize = ""
    @State private var manufacturer = ""
    @State private var lotNumber = ""
    @State private var serialNumber = ""
    @State private var notes = ""
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Column Information")) {
                    TextField("Column Name", text: $name)
                    
                    Picker("Type", selection: $type) {
                        ForEach(ColumnType.allCases, id: \.self) { type in
                            Text(type.displayName).tag(type)
                        }
                    }
                    
                    HStack {
                        TextField("Length (mm)", text: $length)
                            .keyboardType(.decimalPad)
                        TextField("Diameter (mm)", text: $diameter)
                            .keyboardType(.decimalPad)
                    }
                    
                    TextField("Particle Size (μm)", text: $particleSize)
                        .keyboardType(.decimalPad)
                    
                    TextField("Pore Size (Å)", text: $poreSize)
                        .keyboardType(.decimalPad)
                }
                
                Section(header: Text("Manufacturer Information")) {
                    TextField("Manufacturer", text: $manufacturer)
                    TextField("Lot Number", text: $lotNumber)
                    TextField("Serial Number", text: $serialNumber)
                }
                
                Section(header: Text("Notes")) {
                    TextEditor(text: $notes)
                        .frame(minHeight: 100)
                }
            }
            .navigationTitle("Add Column")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(
                leading: Button("Cancel") {
                    presentationMode.wrappedValue.dismiss()
                },
                trailing: Button("Save") {
                    saveColumn()
                }
                .disabled(name.isEmpty || manufacturer.isEmpty || length.isEmpty || diameter.isEmpty || particleSize.isEmpty)
            )
        }
    }
    
    private func saveColumn() {
        guard let lengthValue = Double(length),
              let diameterValue = Double(diameter),
              let particleSizeValue = Double(particleSize) else {
            return
        }
        
        let column = Column(
            name: name,
            type: type,
            dimensions: ColumnDimensions(length: lengthValue, diameter: diameterValue),
            particleSize: particleSizeValue,
            poreSize: Double(poreSize),
            manufacturer: manufacturer,
            lotNumber: lotNumber.isEmpty ? nil : lotNumber,
            serialNumber: serialNumber.isEmpty ? nil : serialNumber,
            notes: notes.isEmpty ? nil : notes
        )
        
        dataManager.addColumn(column)
        presentationMode.wrappedValue.dismiss()
    }
}

struct AddMethodView: View {
    @EnvironmentObject var dataManager: DataManager
    @Environment(\.presentationMode) var presentationMode
    
    @State private var name = ""
    @State private var description = ""
    @State private var selectedColumnId: UUID?
    @State private var flowRate = ""
    @State private var temperature = ""
    @State private var injectionVolume = ""
    @State private var runTime = ""
    @State private var solventA = ""
    @State private var solventB = ""
    @State private var detection = DetectionType.uv
    @State private var notes = ""
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Method Information")) {
                    TextField("Method Name", text: $name)
                    TextField("Description", text: $description)
                    
                    Picker("Column", selection: $selectedColumnId) {
                        Text("Select Column").tag(nil as UUID?)
                        ForEach(dataManager.columns.filter { $0.status == .active }, id: \.id) { column in
                            Text(column.name).tag(column.id as UUID?)
                        }
                    }
                }
                
                Section(header: Text("Parameters")) {
                    TextField("Flow Rate (mL/min)", text: $flowRate)
                        .keyboardType(.decimalPad)
                    
                    TextField("Temperature (°C)", text: $temperature)
                        .keyboardType(.decimalPad)
                    
                    TextField("Injection Volume (μL)", text: $injectionVolume)
                        .keyboardType(.decimalPad)
                    
                    TextField("Run Time (min)", text: $runTime)
                        .keyboardType(.decimalPad)
                }
                
                Section(header: Text("Mobile Phase")) {
                    TextField("Solvent A", text: $solventA)
                    TextField("Solvent B", text: $solventB)
                }
                
                Section(header: Text("Detection")) {
                    Picker("Detection Type", selection: $detection) {
                        ForEach(DetectionType.allCases, id: \.self) { type in
                            Text(type.rawValue).tag(type)
                        }
                    }
                }
                
                Section(header: Text("Notes")) {
                    TextEditor(text: $notes)
                        .frame(minHeight: 100)
                }
            }
            .navigationTitle("Add Method")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(
                leading: Button("Cancel") {
                    presentationMode.wrappedValue.dismiss()
                },
                trailing: Button("Save") {
                    saveMethod()
                }
                .disabled(name.isEmpty || flowRate.isEmpty || injectionVolume.isEmpty || runTime.isEmpty || solventA.isEmpty || solventB.isEmpty)
            )
        }
    }
    
    private func saveMethod() {
        guard let flowRateValue = Double(flowRate),
              let injectionVolumeValue = Double(injectionVolume),
              let runTimeValue = Double(runTime) else {
            return
        }
        
        let selectedColumn = dataManager.columns.first { $0.id == selectedColumnId }
        
        let method = Method(
            name: name,
            description: description.isEmpty ? nil : description,
            columnId: selectedColumnId,
            columnName: selectedColumn?.name,
            flowRate: flowRateValue,
            temperature: Double(temperature),
            injectionVolume: injectionVolumeValue,
            runTime: runTimeValue,
            mobilePhase: MobilePhase(
                solventA: solventA,
                solventB: solventB
            ),
            detection: detection,
            notes: notes.isEmpty ? nil : notes
        )
        
        dataManager.addMethod(method)
        presentationMode.wrappedValue.dismiss()
    }
}

struct AnalyticsView: View {
    @EnvironmentObject var dataManager: DataManager
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Column Utilization Chart
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Column Utilization")
                            .font(.title2)
                            .fontWeight(.bold)
                        
                        ColumnUtilizationChart(data: dataManager.analyticsData.columnUtilization)
                    }
                    .padding()
                    .background(Color(.systemBackground))
                    .cornerRadius(12)
                    .shadow(color: .black.opacity(0.1), radius: 4, x: 0, y: 2)
                    
                    // Method Statistics
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Method Statistics")
                            .font(.title2)
                            .fontWeight(.bold)
                        
                        VStack(spacing: 8) {
                            StatRow(title: "Average Runtime", value: String(format: "%.1f min", dataManager.analyticsData.averageMethodRuntime))
                            StatRow(title: "Most Used Column", value: dataManager.analyticsData.mostUsedColumn ?? "N/A")
                        }
                    }
                    .padding()
                    .background(Color(.systemBackground))
                    .cornerRadius(12)
                    .shadow(color: .black.opacity(0.1), radius: 4, x: 0, y: 2)
                }
                .padding()
            }
            .navigationTitle("Analytics")
            .navigationBarTitleDisplayMode(.large)
        }
    }
}

struct ColumnUtilizationChart: View {
    let data: [ColumnUtilization]
    
    var body: some View {
        VStack(spacing: 8) {
            ForEach(data.sorted { $0.methodCount > $1.methodCount }, id: \.id) { utilization in
                HStack {
                    Text(utilization.columnName)
                        .font(.caption)
                        .frame(width: 80, alignment: .leading)
                    
                    ProgressView(value: Double(utilization.methodCount), total: Double(data.map { $0.methodCount }.max() ?? 1))
                        .progressViewStyle(LinearProgressViewStyle(tint: .blue))
                    
                    Text("\(utilization.methodCount)")
                        .font(.caption)
                        .frame(width: 30, alignment: .trailing)
                }
            }
        }
    }
}

struct StatRow: View {
    let title: String
    let value: String
    
    var body: some View {
        HStack {
            Text(title)
                .foregroundColor(.secondary)
            Spacer()
            Text(value)
                .fontWeight(.medium)
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}