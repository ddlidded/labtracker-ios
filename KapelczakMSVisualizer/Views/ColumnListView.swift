import SwiftUI

struct ColumnListView: View {
    @EnvironmentObject var dataManager: DataManager
    @State private var searchText = ""
    @State private var selectedStatus: ColumnStatus?
    @State private var showingAddColumn = false
    @State private var showingFilter = false
    
    var filteredColumns: [Column] {
        var columns = dataManager.searchColumns(query: searchText)
        if let status = selectedStatus {
            columns = columns.filter { $0.status == status }
        }
        return columns
    }
    
    var body: some View {
        NavigationView {
            VStack {
                // Search and Filter Bar
                HStack {
                    HStack {
                        Image(systemName: "magnifyingglass")
                            .foregroundColor(.secondary)
                        TextField("Search columns...", text: $searchText)
                    }
                    .padding(.horizontal, 12)
                    .padding(.vertical, 8)
                    .background(Color(.systemGray6))
                    .cornerRadius(10)
                    
                    Button(action: {
                        showingFilter = true
                    }) {
                        Image(systemName: "line.3.horizontal.decrease.circle")
                            .foregroundColor(selectedStatus != nil ? .blue : .secondary)
                    }
                }
                .padding(.horizontal)
                
                // Column List
                List {
                    ForEach(filteredColumns) { column in
                        NavigationLink(destination: ColumnDetailView(column: column)) {
                            ColumnRowView(column: column)
                        }
                    }
                    .onDelete(perform: deleteColumns)
                }
                .listStyle(PlainListStyle())
            }
            .navigationTitle("Columns")
            .navigationBarTitleDisplayMode(.large)
            .navigationBarItems(
                trailing: Button(action: {
                    showingAddColumn = true
                }) {
                    Image(systemName: "plus")
                }
            )
            .sheet(isPresented: $showingAddColumn) {
                AddColumnView()
                    .environmentObject(dataManager)
            }
            .actionSheet(isPresented: $showingFilter) {
                ActionSheet(
                    title: Text("Filter by Status"),
                    buttons: [
                        .default(Text("All")) {
                            selectedStatus = nil
                        },
                        .default(Text("Active")) {
                            selectedStatus = .active
                        },
                        .default(Text("Maintenance")) {
                            selectedStatus = .maintenance
                        },
                        .default(Text("Retired")) {
                            selectedStatus = .retired
                        },
                        .default(Text("Damaged")) {
                            selectedStatus = .damaged
                        },
                        .cancel()
                    ]
                )
            }
        }
    }
    
    private func deleteColumns(offsets: IndexSet) {
        for index in offsets {
            let column = filteredColumns[index]
            dataManager.deleteColumn(column)
        }
    }
}

struct ColumnRowView: View {
    let column: Column
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(column.name)
                        .font(.headline)
                        .fontWeight(.semibold)
                    
                    Text(column.type.displayName)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    Text(column.status.rawValue)
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color(column.status.color).opacity(0.2))
                        .foregroundColor(Color(column.status.color))
                        .cornerRadius(8)
                    
                    Text("\(column.methodCount) methods")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Dimensions")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(column.dimensions.displayString)
                        .font(.caption)
                        .fontWeight(.medium)
                }
                
                Spacer()
                
                VStack(alignment: .leading, spacing: 2) {
                    Text("Particle Size")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text("\(column.particleSize, specifier: "%.1f") μm")
                        .font(.caption)
                        .fontWeight(.medium)
                }
                
                Spacer()
                
                VStack(alignment: .leading, spacing: 2) {
                    Text("Manufacturer")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(column.manufacturer)
                        .font(.caption)
                        .fontWeight(.medium)
                }
            }
            
            if let notes = column.notes, !notes.isEmpty {
                Text(notes)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .lineLimit(2)
            }
        }
        .padding(.vertical, 4)
    }
}

struct ColumnListView_Previews: PreviewProvider {
    static var previews: some View {
        ColumnListView()
            .environmentObject(DataManager())
    }
}