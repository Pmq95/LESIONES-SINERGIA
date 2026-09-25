%%writefile app.py
import gradio as gr
import tempfile
import os
from datetime import datetime
import matplotlib.pyplot as plt

# --- BASE DE CONOCIMIENTO (PROTOCOLOS) ---
# Estructura: Tipo de Lesión -> Grado -> Fase -> Lista de Criterios

muscular_fases = {
    "Fase 1: Control Biológico": ["EVA reposo < 3/10", "Edema controlado / Sin derrame", "Cicatriz movilizada sin dolor"],
    "Fase 2: Potenciación Regenerativa": ["Sin dolor en AVD", "Sin derrame tras carga progresiva", "Fuerza simétrica >80-85%"],
    "Fase 3: Potenciación del Movimiento": ["Sin dolor en impactos/cambios dir.", "Sin derrame tras esfuerzos", "Simetría fuerza >90% (LSI)"],
    "Fase 4: Movimiento Global": ["Indoloro en juego real", "Sin inflamación residual post-entreno", "Simetría biomecánica >95%"]
}

PROTOCOLOS = {
    "Lesión Muscular": {
        "Grado I (1-3 sem)": muscular_fases,
        "Grado II (4-8 sem)": muscular_fases,
        "Grado III (8-16+ sem)": muscular_fases
    },
    "Lesión Ligamentosa": {
        "Grado I (1-3 sem)": {
            "Fase 1: Estabilización y acceso": ["Apoyo casi completo", "Marcha funcional", "Dolor y edema descendentes"],
            "Fase 2: Activación y exploración": ["ROM completo o casi completo", "Vida diaria normal", "Mínima reactividad"],
            "Fase 3: Organización y liberación": ["Carrera lineal tolerada", "Buen control monopodal", "Fuerza claramente recuperada"],
            "Fase 4: Integración global y autonomía": ["Sin dolor en deporte", "Sin derrame", "Sin inestabilidad"]
        },
        "Grado II (4-8 sem)": {
            "Fase 1: Estabilización y acceso": ["Apoyo progresivamente completo", "Marcha en clara mejoría", "Sin signos de inestabilidad importante"],
            "Fase 2: Activación y exploración": ["ROM prácticamente completo", "Edema mínimo", "Fuerza básica y control suficientes"],
            "Fase 3: Organización y liberación": ["Vida diaria sin limitación", "Carrera tolerada y saltos sencillos", "Cambios de dirección sin reactividad"],
            "Fase 4: Integración global y autonomía": ["Estabilidad percibida en pista", "Confianza en el gesto", "Tolerancia a la carga repetida"]
        },
        "Grado III (8-16+ sem)": {
            "Fase 1: Estabilización y acceso": ["Disminución clara de irritabilidad", "Mejor tolerancia al apoyo", "Evolución estable sin empeoramiento"],
            "Fase 2: Activación y exploración": ["Marcha funcional", "ROM útil y cada vez más completo", "Buena respuesta a la carga protegida"],
            "Fase 3: Organización y liberación": ["Control para tareas exigentes", "Ausencia de inestabilidad franca", "Capacidad funcional en crecimiento"],
            "Fase 4: Integración global y autonomía": ["Cumplimiento de criterios clínicos", "Estabilidad funcional confirmada", "Retorno progresivo exitoso"]
        }
    }
}

def update_ui(tipo, grado):
    fases = PROTOCOLOS[tipo][grado]
    updates = []
    for nombre_fase, criterios in fases.items():
        updates.append(gr.update(label=nombre_fase, choices=criterios, value=[]))
    return updates

def process_dashboard(patient_name, tipo, grade, cb1, cb2, cb3, cb4):
    fases = PROTOCOLOS[tipo][grade]
    nombres_fases = list(fases.keys())

    total_checked = len(cb1) + len(cb2) + len(cb3) + len(cb4)
    total_items = 12 # 3 por fase x 4 fases
    pct = int((total_checked / total_items) * 100)

    # Lógica de fases
    current_phase_idx = 0
    if len(cb1) == 3:
        current_phase_idx = 1
        if len(cb2) == 3:
            current_phase_idx = 2
            if len(cb3) == 3:
                current_phase_idx = 3
                if len(cb4) == 3:
                    current_phase_idx = 4 # Completado

    if current_phase_idx < 4:
        estado = nombres_fases[current_phase_idx]
    else:
        estado = "Alta Clínica y Deportiva 🎉"

    # HTML Visual para la App (Corregido color de texto)
    html_output = f"""
    <div style="padding:20px; border: 2px solid #1a237e; border-radius: 12px; background-color: #f8f9fa; color: #212121;">
        <h2 style="color: #1a237e; margin-top:0;">Paciente: {patient_name if patient_name else 'No especificado'}</h2>
        <h3 style="color: #2e7d32;">Progreso Total: {pct}%</h3>
        <h3 style="color: #e65100;">ESTADO ACTUAL: {estado}</h3>
        <p style="color: #212121; font-size: 16px;"><i>Criterios superados: {total_checked} de {total_items}</i></p>
    </div>
    """

    # Generar texto para el informe descargable
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    report_text = f"INFORME DE PROGRESIÓN - {tipo.upper()}\n"
    report_text += f"=========================================\n"
    report_text += f"Fecha: {date_str}\n"
    report_text += f"Paciente: {patient_name if patient_name else 'No especificado'}\n"
    report_text += f"Grado de Lesión: {grade}\n"
    report_text += f"Progreso Total: {pct}% ({total_checked}/{total_items} criterios)\n"
    report_text += f"Fase Clínica Actual: {estado}\n"

    # Nombres de archivos seguros
    temp_dir = tempfile.gettempdir()
    safe_name = patient_name.replace(" ", "_") if patient_name else "paciente"
    file_path_txt = os.path.join(temp_dir, f"informe_{safe_name}.txt")
    file_path_img = os.path.join(temp_dir, f"grafico_{safe_name}.png")

    # Guardar TXT
    with open(file_path_txt, "w", encoding="utf-8") as f:
        f.write(report_text)

    # Generar Gráfico Visual (Matplotlib)
    fig, ax = plt.subplots(figsize=(8, 2.5))
    ax.barh([0], [pct], color='#4caf50' if pct == 100 else '#2196f3', height=0.4)
    ax.barh([0], [100], color='#e0e0e0', height=0.4, zorder=0)
    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
    ax.set_title(f"Progreso de Rehabilitación: {pct}%\n({total_checked}/{total_items} criterios)", color='#1a237e', fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    plt.tight_layout()

    # Guardar Gráfico PNG
    fig.savefig(file_path_img, dpi=300, bbox_inches='tight')
    plt.close(fig)

    return html_output, fig, [file_path_txt, file_path_img]

# Crear la interfaz con Gradio Blocks
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📋 Panel Clínico de Progresión de Lesiones")
    gr.Markdown("Selecciona el tipo de lesión y el grado. Los criterios se actualizarán automáticamente. Marca los hitos superados para calcular el progreso.")

    with gr.Row():
        patient_input = gr.Textbox(label="Nombre del Paciente", placeholder="Ej. Carlos López")
        tipo_input = gr.Dropdown(choices=list(PROTOCOLOS.keys()), value="Lesión Muscular", label="Tipo de Lesión")
        grade_input = gr.Dropdown(choices=list(PROTOCOLOS["Lesión Muscular"].keys()), value='Grado I (1-3 sem)', label="Grado de Lesión")

    # Grupos de Checkboxes para las 4 Fases
    cb_fases = []
    with gr.Row():
        for i in range(4):
            with gr.Column():
                cb = gr.CheckboxGroup(label=f"Fase {i+1}", choices=[], interactive=True)
                cb_fases.append(cb)

    with gr.Row():
        calc_btn = gr.Button("Actualizar Estado y Generar Informe", variant="primary")

    with gr.Row():
        with gr.Column(scale=2):
            out_html = gr.HTML()
        with gr.Column(scale=1):
            out_plot = gr.Plot(label="Gráfico de Progreso Visual")
            out_file = gr.File(label="Descargar Informes (TXT y PNG)", file_count="multiple")

    # Eventos de actualización dinámica
    tipo_input.change(fn=update_ui, inputs=[tipo_input, grade_input], outputs=cb_fases)
    grade_input.change(fn=update_ui, inputs=[tipo_input, grade_input], outputs=cb_fases)

    # Inicializar la UI al cargar
    demo.load(fn=update_ui, inputs=[tipo_input, grade_input], outputs=cb_fases)

    # Acción del botón
    inputs = [patient_input, tipo_input, grade_input] + cb_fases
    calc_btn.click(fn=process_dashboard, inputs=inputs, outputs=[out_html, out_plot, out_file])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)

