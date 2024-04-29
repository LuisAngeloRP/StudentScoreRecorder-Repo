import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QDateEdit,
    QSizePolicy,
    QHeaderView,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QDate
import pandas as pd


class MiVentana(QWidget):
    def __init__(self):
        super().__init__()

        self.estudiantes = [
            {
                "apellido": "Adauto Huaman",
                "nombre": "Isaac",
                "correo": "isaac.adauto.h@uni.pe",
            },
            {
                "apellido": "Alvarado Osorio",
                "nombre": "Alexander Oliver",
                "correo": "alexander.alvarado.o@uni.pe",
            },
            {
                "apellido": "Alvarez Huaringa",
                "nombre": "Sandro Enrique",
                "correo": "sandro.alvarez.h@uni.pe",
            },
            {
                "apellido": "Andia Fernandez",
                "nombre": "Diego Paolo",
                "correo": "diego.andia.f@uni.pe",
            },
            {
                "apellido": "Aymachoque Aymachoque",
                "nombre": "Luis Jairo",
                "correo": "luis.aymachoque.a@uni.pe",
            },
            {
                "apellido": "Ballarta Ulloa",
                "nombre": "Natalia Paula",
                "correo": "natalia.ballarta.u@uni.pe",
            },
            {
                "apellido": "Bravo Olano",
                "nombre": "Randy Piero",
                "correo": "rbravo@uni.pe",
            },
            {
                "apellido": "Callupe Pardo",
                "nombre": "Yoselyn Patricia",
                "correo": "yoselyn.callupe.p@uni.pe",
            },
            {
                "apellido": "Carhuas Romero",
                "nombre": "Jhon Jesus",
                "correo": "jhon.carhuas.r@uni.pe",
            },
            {
                "apellido": "Chávez Arifaela",
                "nombre": "Niels Mauro",
                "correo": "niels.chavez.a@uni.pe",
            },
            {
                "apellido": "Del Rio Gutierrez",
                "nombre": "Jairo Kazuo",
                "correo": "jairo.delrio.g@uni.pe",
            },
            {
                "apellido": "Dionicio Achachagua",
                "nombre": "Cesar Alonso",
                "correo": "cesar.dionicio.a@uni.pe",
            },
            {
                "apellido": "Farfan Esteban",
                "nombre": "Gabriel Martin",
                "correo": "gabriel.farfan.e@uni.pe",
            },
            {
                "apellido": "Flores Dalia",
                "nombre": "Gerson Donato",
                "correo": "gfloresd@uni.pe",
            },
            {
                "apellido": "Flores Velarde",
                "nombre": "Roberto Carlos",
                "correo": "roberto.flores.v@uni.pe",
            },
            {
                "apellido": "Leon Sanchez",
                "nombre": "Fransua Mijail",
                "correo": "fransua.leon.s@uni.pe",
            },
            {
                "apellido": "Mallma Orihuela",
                "nombre": "Gherson Bryan",
                "correo": "gherson.mallma.o@uni.pe",
            },
            {
                "apellido": "Mallma Pardo",
                "nombre": "Telesforo",
                "correo": "tmallmap@uni.pe",
            },
            {
                "apellido": "Meza Alvino",
                "nombre": "Fabian Alessandro Moises",
                "correo": "fabian.meza.a@uni.pe",
            },
            {
                "apellido": "Montes Lozano",
                "nombre": "Diego Martin",
                "correo": "diego.montes.l@uni.pe",
            },
            {
                "apellido": "Nuñez Poma",
                "nombre": "Robert Gianpierro Jesus",
                "correo": "robert.nunez.p@uni.pe",
            },
            {
                "apellido": "Palacios Palacios",
                "nombre": "Rafael Enrique",
                "correo": "rafael.palacios.p@uni.pe",
            },
            {
                "apellido": "Palomino Valdivia",
                "nombre": "Erick Da Silva",
                "correo": "erick.palomino.v@uni.pe",
            },
            {
                "apellido": "Quispe Mitma",
                "nombre": "Cesar Fernando",
                "correo": "cesar.quispe.m@uni.pe",
            },
            {
                "apellido": "Quispe Rojas",
                "nombre": "Alfredo Martin",
                "correo": "alfredo.quispe.r@uni.pe",
            },
            {
                "apellido": "Quispe Tenorio",
                "nombre": "Ximena Lucia",
                "correo": "ximena.quispe.t@uni.pe",
            },
            {
                "apellido": "Ramirez Villaverde",
                "nombre": "Oscar Leonardo",
                "correo": "oscar.ramirez.v@uni.pe",
            },
            {
                "apellido": "Rodriguez Inga",
                "nombre": "Fernando Frans",
                "correo": "frodriguezi@uni.pe",
            },
            {
                "apellido": "Salirrosas Avila",
                "nombre": "Sebastian Jose",
                "correo": "sebastian.salirrosas.a@uni.pe",
            },
            {
                "apellido": "Soto Cossio",
                "nombre": "Edwin Isaac",
                "correo": "edwin.soto.c@uni.pe",
            },
            {
                "apellido": "Urbano Chocce",
                "nombre": "Yeison Stiven",
                "correo": "yeison.urbano.c@uni.pe",
            },
            {
                "apellido": "Valencia Grey",
                "nombre": "William Gerardo",
                "correo": "william.valencia.g@uni.pe",
            },
            {
                "apellido": "Valerio Contreras",
                "nombre": "Cristhian Jesus",
                "correo": "cristhian.valerio.c@uni.pe",
            },
            {
                "apellido": "Velasquez Solis",
                "nombre": "Walter Antonio",
                "correo": "walter.velasquez.s@uni.pe",
            },
            {
                "apellido": "Villanueva Reyes",
                "nombre": "Juan Axel",
                "correo": "juan.villanueva.r@uni.pe",
            },
        ]

        # Crear widgets
        self.label_titulo = QLabel(
            "Registrador de Puntos SI605U Arquitectura Empresarial"
        )
        self.label_titulo.setAlignment(Qt.AlignCenter)
        self.label_titulo.setStyleSheet("font-size: 24px; font-weight: bold;")

        # Cuadro desplegable para seleccionar fecha
        self.fecha_edit = QDateEdit(self)
        self.fecha_edit.setCalendarPopup(True)
        self.fecha_edit.setDate(
            QDate.currentDate()
        )  # Establecer la fecha actual por defecto
        self.fecha_edit.setFixedSize(150, 30)  # Tamaño más pequeño horizontalmente
        self.fecha_edit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Conectar cambio de fecha a la función cambiar_fecha
        self.fecha_edit.dateChanged.connect(self.cambiar_fecha)

        # Botones adicionales
        self.btn_registrar = QPushButton("Registrar Puntaje", self)
        self.btn_registrar.setFixedSize(120, 30)  # Ajustar el tamaño del botón

        # Conectar botones a funciones
        self.btn_registrar.clicked.connect(self.registrar)

        # Diseño horizontal para los botones adicionales y el cuadro de fecha
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.fecha_edit)
        button_layout.addStretch(
            1
        )  # Añadir espacio elástico para empujar el botón a la derecha
        button_layout.addWidget(self.btn_registrar)

        # Verificar si el archivo Excel existe
        try:
            pd.ExcelFile("Registro_Puntaje_SI650U.xlsx").sheet_names
        except FileNotFoundError:
            # Si no existe, crear el DataFrame con las columnas necesarias y datos iniciales

            self.crear_columnas_excel()

        self.excel_data = None
        # Crear la tabla de asistencia
        self.crear_tabla_asistencia()

        # Configurar diseño
        layout = QVBoxLayout()
        layout.addWidget(self.label_titulo)
        layout.addLayout(
            button_layout
        )  # Diseño horizontal para botones adicionales y cuadro de fecha
        layout.addWidget(self.tabla_asistencia)
        self.setLayout(layout)

        # Configurar ventana
        self.setWindowTitle("Registrador de Puntos")
        self.setFixedSize(900, 700)
        self.move(570, 180)  # Mover más a la izquierda

    def crear_tabla_asistencia(self):
        # Crear la tabla de asistencia
        self.tabla_asistencia = QTableWidget(
            len(self.estudiantes), 4
        )  # Ahora 4 columnas
        self.tabla_asistencia.setHorizontalHeaderLabels(
            ["Alumno", "Puntaje", "Asignar Punto", "Quitar Punto"]
        )

        # Obtener fechas existentes del archivo Excel
        self.actualizar_fechas_existentes()

        for i, estudiante in enumerate(self.estudiantes):
            apellido_nombre = f"{estudiante['apellido']} {estudiante['nombre']}"
            item_nombre = QTableWidgetItem(apellido_nombre)
            item_puntaje = QTableWidgetItem("0")

            # Bloquear las celdas de "Apellido", "Nombre" y "Puntaje"
            item_nombre.setFlags(item_nombre.flags() ^ Qt.ItemIsEditable)
            item_puntaje.setFlags(item_puntaje.flags() ^ Qt.ItemIsEditable)

            self.tabla_asistencia.setItem(i, 0, item_nombre)
            self.tabla_asistencia.setItem(i, 1, item_puntaje)

            boton_asignar = QPushButton("Asignar Punto", self)
            boton_quitar = QPushButton("Quitar Punto", self)

            boton_asignar.clicked.connect(
                lambda _, row=i: self.actualizar_puntaje(row, 1)
            )
            boton_quitar.clicked.connect(
                lambda _, row=i: self.actualizar_puntaje(row, -1)
            )

            self.tabla_asistencia.setCellWidget(i, 2, boton_asignar)
            self.tabla_asistencia.setCellWidget(i, 3, boton_quitar)

        # Ajustar tamaño de las celdas
        self.tabla_asistencia.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch
        )
        self.tabla_asistencia.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Fixed
        )
        self.tabla_asistencia.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.Fixed
        )
        self.tabla_asistencia.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.Fixed
        )

        # Bloquear las columnas "Apellido", "Nombre" y "Puntaje" para edición directa
        for i in range(self.tabla_asistencia.columnCount()):
            if i != 2 and i != 3:  # No bloquear "Asignar Punto" y "Quitar Punto"
                self.tabla_asistencia.item(0, i).setFlags(Qt.ItemIsEnabled)

        # Mostrar las fechas existentes en el programa
        self.mostrar_fechas_existentes()

    def actualizar_fechas_existentes(self):
        # Obtener fechas existentes del archivo Excel
        try:
            self.excel_data = pd.read_excel(
                "Registro_Puntaje_SI650U.xlsx", sheet_name="Registros", index_col=0
            )
            fechas_existentes = list(self.excel_data.columns)
        except FileNotFoundError:
            fechas_existentes = []

        self.fechas_existentes = fechas_existentes

    def mostrar_fechas_existentes(self):
        # Mostrar las fechas existentes en el programa
        fecha_actual = self.fecha_edit.date().toString("dd/MM/yyyy")
        if fecha_actual in self.fechas_existentes:
            index = self.fechas_existentes.index(fecha_actual)
            for i in range(self.tabla_asistencia.rowCount()):
                if index < len(self.fechas_existentes):
                    puntaje_excel = self.excel_data.iloc[i, index]
                    self.tabla_asistencia.item(i, 1).setText(str(puntaje_excel))
        else:
            # Si la fecha actual no está en las fechas existentes, poner todos los puntajes en 0
            for i in range(self.tabla_asistencia.rowCount()):
                self.tabla_asistencia.item(i, 1).setText("0")

    def cambiar_fecha(self):
        # Método llamado al cambiar la fecha en el cuadro desplegable
        self.mostrar_fechas_existentes()

    def crear_columnas_excel(self):
        # Crear un DataFrame con las columnas necesarias y datos iniciales
        columnas = ["Apellidos", "Nombres", "Correo"]
        datos_iniciales = [
            {
                "Apellidos": estudiante["apellido"],
                "Nombres": estudiante["nombre"],
                "Correo": estudiante["correo"],
            }
            for estudiante in self.estudiantes
        ]
        df = pd.DataFrame(datos_iniciales, columns=columnas)

        # Guardar el DataFrame en un archivo Excel
        df.to_excel("Registro_Puntaje_SI650U.xlsx", index=False, sheet_name="Registros")

    def actualizar_puntaje(self, fila, cantidad):
        item_puntaje = self.tabla_asistencia.item(fila, 1)
        puntaje_actual = int(item_puntaje.text())
        nuevo_puntaje = puntaje_actual + cantidad
        item_puntaje.setText(str(nuevo_puntaje))

    def registrar(self):
        # Crear un DataFrame con los datos de la tabla
        data = []
        fecha_actual = self.fecha_edit.date().toString("dd/MM/yyyy")

        for i in range(self.tabla_asistencia.rowCount()):
            puntaje = self.tabla_asistencia.item(i, 1).text()
            data.append({fecha_actual: puntaje})

        df = pd.DataFrame(data)

        # Cargar el archivo Excel existente (si existe)
        existing_df = pd.read_excel(
            "Registro_Puntaje_SI650U.xlsx", sheet_name="Registros"
        )

        # Concatenar el nuevo DataFrame con el existente
        df_merged = pd.concat([existing_df, df], axis=1)

        # Guardar el DataFrame en un archivo Excel
        df_merged.to_excel(
            "Registro_Puntaje_SI650U.xlsx", sheet_name="Registros", index=False
        )

        # Mostrar mensaje de puntajes registrados correctamente
        mensaje = f"Puntajes de la fecha {fecha_actual} correctamente registrados"
        QMessageBox.information(self, "Puntaje Registrado", mensaje)


if __name__ == "__main__":
    # Crear la aplicación
    app = QApplication(sys.argv)

    # Crear e mostrar la ventana
    ventana = MiVentana()
    ventana.show()

    # Ejecutar la aplicación
    sys.exit(app.exec_())
