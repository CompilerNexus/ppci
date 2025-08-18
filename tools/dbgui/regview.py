from qtwrapper import Qt, QtCore, QtWidgets


class RegisterModel(QtCore.QAbstractTableModel):
    def __init__(self, debugger):
        super().__init__()
        self.debugger = debugger
        self._registers = self.debugger.debugger.registers
        self._register_values = {}
        self.debugger.stopped.connect(self.on_stopped)
        self.headers = ("Register", "Value")

    def on_stopped(self):
        from_index = self.index(0, 1)
        to_index = self.index(len(self._registers) - 1, 1)
        self._register_values = self.debugger.debugger.get_register_values(
            self._registers
        )
        self.dataChanged.emit(from_index, to_index)

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return len(self._registers)

    def columnCount(self, parent):
        if parent.isValid():
            return 0
        return len(self.headers)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]

    def data(self, index, role):
        if index.isValid():
            row, col = index.row(), index.column()
            if role == Qt.DisplayRole:
                register = self._registers[row]
                if col == 0:
                    return register.name
                elif col == 1:
                    if register in self._register_values:
                        value = self._register_values[register]
                    else:
                        value = 0
                    return f"0x{value:X}"

    def setData(self, index, value, role):
        if index.isValid():
            row = index.row()
            col = index.column()
            if role == Qt.EditRole and col == 1:
                value = int(value, 16)
                register = self._registers[row]
                self.debugger.debugger.set_register(register, value)
                return True
        return False

    def flags(self, index):
        if index.isValid():
            col = index.column()
            if col == 1:
                return super().flags(index) | Qt.ItemIsEditable
        return super().flags(index)


class RegisterView(QtWidgets.QTableView):
    def __init__(self, debugger):
        super().__init__()
        self.mdl = RegisterModel(debugger)
        self.setModel(self.mdl)
        self.horizontalHeader().setStretchLastSection(True)

        # Connect signals:
        debugger.halted.connect(self.setEnabled)
