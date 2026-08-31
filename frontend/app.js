document.getElementById('prediction-form').addEventListener('submit', async (e) => {
    e.preventDefault(); // Evita que la página se recargue

    // Referencias a los elementos visuales
    const btnCalcular = e.target.querySelector('button');
    const loading = document.getElementById('loading');
    const resultadoContainer = document.getElementById('resultado-container');
    const estadoInicial = document.getElementById('estado-inicial');
    const precioFinal = document.getElementById('precio-final');

    // Activar estado de carga (UX)
    btnCalcular.disabled = true;
    btnCalcular.classList.add('opacity-50', 'cursor-not-allowed');
    estadoInicial.classList.add('hidden');
    resultadoContainer.classList.add('hidden');
    loading.classList.remove('hidden');

    // Recolectar datos del formulario
    const payload = {
        posicion: document.getElementById('posicion').value,
        age: parseFloat(document.getElementById('edad').value),
        minutes_played: parseInt(document.getElementById('minutos').value),
        goals: parseInt(document.getElementById('goles').value),
        asistencias: parseInt(document.getElementById('asistencias').value)
    };

    try {
        // Enviar datos a nuestra API (El cerebro XGBoost)
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error('Error en el servidor');

        const data = await response.json();
        
        // Formatear el precio estilo europeo (ej: 4.762.642)
        const precioFormateado = new Intl.NumberFormat('es-ES').format(data.valor_justo_estimado_eur);
        
        // Mostrar resultado en la UI
        precioFinal.textContent = precioFormateado;
        loading.classList.add('hidden');
        resultadoContainer.classList.remove('hidden');
    } catch (error) {
        console.error('Error:', error);
        alert('Hubo un problema calculando el valor. Revisa la consola.');
        loading.classList.add('hidden');
        estadoInicial.classList.remove('hidden');
    } finally {
        // Restaurar el botón
        btnCalcular.disabled = false;
        btnCalcular.classList.remove('opacity-50', 'cursor-not-allowed');
    }
});
