import gradio as gr
import tempfile
import os
from datetime import datetime
import matplotlib.pyplot as plt

# Definir los criterios por cada fase
criteria = {
    "Fase 1: Protección y Activación": [
        "Inflamación y dolor basal controlados",
        "Caminar sin dolor (marcha funcional)",
        "Contracción isométrica sin dolor agudo"
    ],
    "Fase 2: Restauración ROM y Fuerza": [
        "Rango de Movimiento (ROM) completo y sin dolor",
        "Fuerza simétrica en test manual (baja intensidad)",
        "Tolerancia a carga isotónica progresiva (ej. sentadilla)"
    ],
    "Fase 3: Progresión Excéntrica": [
        "Fuerza Excéntrica (ej. Nordic/Slider) con LSI > 85%",
        "Tolerancia a elongación máxima sin dolor",
        "Tolerancia a carrera lineal suave"
    ],
    "Fase 4: Alta Velocidad y RTS": [
        "LSI general de fuerza > 95%",
        "Sprint al 100% VMax sin reactividad ni dolor",
        "Agilidad compleja y cambios de dirección (cuts) tolerados"
    ]
}

def process_dashboard(patient_name, grade, *checkbox_values):
    total_checked = sum(checkbox_values)
    total_items = 12
    pct = int((total_checked / total_items) * 100)

    # Lógica de fases
    current_phase = 1
    if all(checkbox_values[0:3]):
        current_phase = 2
        if all(checkbox_values[3:6]):
            current_phase = 3
            if all(checkbox_values[6:9]):
                current_phase = 4
                if all(checkbox_values[9:12]):
                    current_phase = 5

    if current_phase == 1:
        estado = "Fase 1: Protección y Activación"
        puede = "Reposo relativo, aplicar hielo/compresión, caminar suavemente, ejercicios isométricos sin dolor."
        no_puede = "Estiramientos del músculo lesionado, correr, cargar peso, masajes profundos tempranos."
    elif current_phase == 2:
        estado = "Fase 2: Restauración ROM y Fuerza"
        puede = "Ejercicios isotónicos ligeros, estiramientos suaves e indoloros, bicicleta estática, nado."
        no_puede = "Trabajo excéntrico intenso, sprints, saltos, cambios de dirección."
    elif current_phase == 3:
        estado = "Fase 3: Progresión Excéntrica"
        puede = "Trabajo de fuerza excéntrica (Nordic, etc.), carrera lineal a velocidad moderada, ejercicios de fuerza general."
        no_puede = "Sprints a máxima velocidad (VMax), competiciones, movimientos explosivos imprevisibles."
    elif current_phase == 4:
        estado = "Fase 4: Alta Velocidad y Retorno al Deporte (RTS)"
        puede = "Sprints progresivos, ejercicios de agilidad, entrenamientos tácticos/específicos del deporte."
        no_puede = "Retornar a competición oficial hasta confirmar simetría LSI > 95% y ausencia total de reactividad."
    else:
        estado = "Alta Deportiva (RTS Completo) 🎉"
        puede = "Competición oficial, máxima exigencia deportiva."
        no_puede = "No se debe abandonar el trabajo preventivo de fuerza excéntrica."

    # HTML Visual para la App
    html_output = f"""
    <div style="padding:20px; border: 2px solid #1a237e; border-radius: 12px; background-color: #f8f9fa;">
        <h2 style="color: #1a237e; margin-top:0;">Paciente: {patient_name if patient_name else 'No especificado'}</h2>
        <h3 style="color: #2e7d32;">Progreso Total: {pct}%</h3>
        <h3 style="color: #e65100;">ESTADO ACTUAL: {estado}</h3>
        <p style="font-size: 16px;"><span style="font-size: 20px;">🟢</span> <b>PUEDE HACER:</b><br> {puede}</p>
        <p style="font-size: 16px;"><span style="font-size: 20px;">🔴</span> <b>NO DEBE HACER:</b><br> {no_puede}</p>
    </div>
    """

    # Generar texto para el informe descargable
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    report_text = f"INFORME DE PROGRESIÓN - LESIÓN MUSCULAR\n"
    report_text += f"=========================================\n"
    report_text += f"Fecha: {date_str}\n"
    report_text += f"Paciente: {patient_name if patient_name else 'No especificado'}\n"
    report_text += f"Grado de Lesión: {grade}\n"
    report_text += f"Progreso Total: {pct}% ({total_checked}/{total_items} criterios)\n"
    report_text += f"Fase Clínica Actual: {estado}\n\n"
    report_text += f"RECOMENDACIONES CLÍNICAS\n"
    report_text += f"-----------------------------------------\n"
    report_text += f"[+] PUEDE HACER: {puede}\n"
    report_text += f"[-] NO DEBE HACER: {no_puede}\n"

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
    gr.Markdown("# 📋 Panel Clínico: Progresión de Lesiones Musculares")
    gr.Markdown("Genera informes personalizados y evalúa el progreso basado en hitos fisiológicos.")

    with gr.Row():
        patient_input = gr.Textbox(label="Nombre del Paciente", placeholder="Ej. Carlos López")
        grade_input = gr.Dropdown(choices=['Grado I (1-3 sem)', 'Grado II (4-8 sem)', 'Grado III (8-16+ sem)'], value='Grado I (1-3 sem)', label="Grado de Lesión")

    cb_inputs = []
    with gr.Row():
        for phase, items in criteria.items():
            with gr.Column():
                gr.Markdown(f"### {phase}")
                for item in items:
                    cb = gr.Checkbox(label=item, value=False)
                    cb_inputs.append(cb)

    with gr.Row():
        calc_btn = gr.Button("Actualizar Estado y Generar Informe", variant="primary")

    with gr.Row():
        with gr.Column(scale=2):
            out_html = gr.HTML()
        with gr.Column(scale=1):
            out_plot = gr.Plot(label="Gráfico de Progreso Visual")
            out_file = gr.File(label="Descargar Informes (TXT y PNG)", file_count="multiple")

    inputs = [patient_input, grade_input] + cb_inputs
    calc_btn.click(fn=process_dashboard, inputs=inputs, outputs=[out_html, out_plot, out_file])

if __name__ == "__main__":
    # Configuramos el host y el puerto dinámico necesario para servicios cloud como Render
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
