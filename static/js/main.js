document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations
    initializeAnimations();
    
    // Initialize modals
    initializeModals();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize search functionality
    initializeSearch();
    
    // Initialize auto-refresh for health check
    initializeAutoRefresh();
    
    // Initialize theme toggle
    initializeThemeToggle();
});

function initializeAnimations() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card, .server-card, .status-item');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
    
    // Add hover effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

function initializeModals() {
    // Modal functionality
    const modals = document.querySelectorAll('.modal');
    const modalTriggers = document.querySelectorAll('[data-modal-target]');
    const modalCloses = document.querySelectorAll('[data-modal-close]');
    
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('data-modal-target');
            const modal = document.getElementById(targetId);
            if (modal) {
                showModal(modal);
            }
        });
    });
    
    modalCloses.forEach(close => {
        close.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                hideModal(modal);
            }
        });
    });
    
    // Close modal when clicking outside
    modals.forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                hideModal(this);
            }
        });
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                hideModal(openModal);
            }
        }
    });
}

function showModal(modal) {
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
    
    // Focus on first input if available
    const firstInput = modal.querySelector('input, textarea, select');
    if (firstInput) {
        setTimeout(() => firstInput.focus(), 100);
    }
}

function hideModal(modal) {
    modal.classList.remove('show');
    document.body.style.overflow = '';
}

function initializeTooltips() {
    // Simple tooltip implementation
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltipText = this.getAttribute('data-tooltip');
            const tooltip = createTooltip(tooltipText);
            document.body.appendChild(tooltip);
            positionTooltip(tooltip, this);
        });
        
        element.addEventListener('mouseleave', function() {
            const tooltip = document.querySelector('.tooltip');
            if (tooltip) {
                tooltip.remove();
            }
        });
    });
}

function createTooltip(text) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: absolute;
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 12px;
        z-index: 10000;
        pointer-events: none;
        white-space: nowrap;
    `;
    return tooltip;
}

function positionTooltip(tooltip, element) {
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
}

function initializeSearch() {
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const searchableItems = document.querySelectorAll('.server-card, .log-line');
            
            searchableItems.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.style.display = '';
                    item.classList.add('highlight');
                } else {
                    item.style.display = 'none';
                    item.classList.remove('highlight');
                }
            });
        });
    }
}

function initializeAutoRefresh() {
    // Auto-refresh for health check page
    if (window.location.pathname === '/health') {
        let refreshInterval;
        const refreshButton = document.querySelector('.refresh-btn');
        
        if (refreshButton) {
            // Add auto-refresh toggle
            const autoRefreshToggle = document.createElement('label');
            autoRefreshToggle.innerHTML = `
                <input type="checkbox" id="auto-refresh"> Auto-refresh (30s)
            `;
            autoRefreshToggle.style.marginLeft = '20px';
            refreshButton.parentNode.appendChild(autoRefreshToggle);
            
            const checkbox = document.getElementById('auto-refresh');
            checkbox.addEventListener('change', function() {
                if (this.checked) {
                    startAutoRefresh();
                } else {
                    stopAutoRefresh();
                }
            });
        }
        
        function startAutoRefresh() {
            refreshInterval = setInterval(() => {
                window.location.reload();
            }, 30000);
        }
        
        function stopAutoRefresh() {
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
        }
    }
}

function initializeThemeToggle() {
    // Add theme toggle button
    const themeToggle = document.createElement('button');
    themeToggle.innerHTML = '🌙';
    themeToggle.className = 'floating-action theme-toggle';
    themeToggle.style.right = '100px';
    themeToggle.setAttribute('data-tooltip', 'Toggle Dark Mode');
    document.body.appendChild(themeToggle);
    
    // Check for saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        themeToggle.innerHTML = '☀️';
    }
    
    themeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-theme');
        const isDark = document.body.classList.contains('dark-theme');
        
        this.innerHTML = isDark ? '☀️' : '🌙';
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        animation: slideInRight 0.3s ease;
    `;
    
    // Set background color based on type
    const colors = {
        info: '#3498db',
        success: '#27ae60',
        warning: '#f39c12',
        error: '#e74c3c'
    };
    notification.style.background = colors[type] || colors.info;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(date) {
    return new Date(date).toLocaleString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Enhanced log viewer functionality
function initializeLogViewer() {
    const logViewer = document.querySelector('.log-viewer');
    if (logViewer) {
        // Add line numbers
        const lines = logViewer.querySelectorAll('.log-line');
        lines.forEach((line, index) => {
            const lineNumber = document.createElement('span');
            lineNumber.className = 'line-number';
            lineNumber.textContent = (index + 1).toString().padStart(3, '0');
            lineNumber.style.cssText = `
                color: #666;
                margin-right: 15px;
                font-family: monospace;
                user-select: none;
            `;
            line.insertBefore(lineNumber, line.firstChild);
        });
        
        // Add copy functionality
        const copyButton = document.createElement('button');
        copyButton.innerHTML = '📋 Copy All';
        copyButton.className = 'btn btn-outline';
        copyButton.style.marginBottom = '10px';
        
        copyButton.addEventListener('click', function() {
            const text = Array.from(lines).map(line => line.textContent).join('\n');
            navigator.clipboard.writeText(text).then(() => {
                showNotification('Logs copied to clipboard!', 'success');
            });
        });
        
        logViewer.parentNode.insertBefore(copyButton, logViewer);
    }
}

// Call log viewer initialization if on log page
if (window.location.pathname.includes('/ver_log/')) {
    document.addEventListener('DOMContentLoaded', initializeLogViewer);
}

// Modal para selección de archivos remotos
function mostrarModalSeleccionArchivo(datosConexion, rutaInicial = '/') {
    // Crear modal si no existe
    let modal = document.getElementById('modalSeleccionArchivo');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'modalSeleccionArchivo';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100vw';
        modal.style.height = '100vh';
        modal.style.background = 'rgba(0,0,0,0.4)';
        modal.style.display = 'flex';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        modal.style.zIndex = '9999';
        modal.innerHTML = `
            <div style="background: #fff; padding: 2.5rem 2rem 2rem 2rem; border-radius: 14px; min-width: 370px; max-width: 98vw; max-height: 85vh; overflow-y: auto; box-shadow: 0 8px 40px #0003; border: 2px solid #007bff33;">
                <h3 style='margin-bottom:1.2rem; color:#007bff; display:flex; align-items:center; gap:0.5rem;'><span style='font-size:1.3em;'>📂</span> Selecciona un archivo de log</h3>
                <div style='margin-bottom:1rem; display:flex; gap:0.5rem; align-items:center;'>
                    <input id="inputRutaRemota" type="text" placeholder="/var/log" style="flex:1; padding:0.5rem 0.8rem; border-radius:6px; border:1px solid #bbb; font-size:1em;" />
                    <button class="volt-btn volt-btn-info" style="padding:0.4rem 1rem; font-size:1em;" onclick="navegarARutaRemota()">Ir</button>
                </div>
                <div id="navegadorArchivosRemoto" style="margin-bottom:1.2rem;"></div>
                <button id="cerrarModalSeleccionArchivo" class="volt-btn volt-btn-outline-primary" style="margin-top:1rem; float:right;">Cerrar</button>
            </div>
        `;
        document.body.appendChild(modal);
        document.getElementById('cerrarModalSeleccionArchivo').onclick = () => modal.remove();
        document.getElementById('inputRutaRemota').addEventListener('keydown', function(e) {
            if (e.key === 'Enter') navegarARutaRemota();
        });
    } else {
        modal.style.display = 'flex';
    }
    document.getElementById('inputRutaRemota').value = rutaInicial;
    window._rutaRemotaActual = rutaInicial;
    cargarArchivosRemotos(datosConexion, rutaInicial);
}

function navegarARutaRemota() {
    const ruta = document.getElementById('inputRutaRemota').value.trim();
    if (ruta) {
        window._rutaRemotaActual = ruta;
        cargarArchivosRemotos(window._datosConexionRemoto, ruta);
    }
}

function cargarArchivosRemotos(datosConexion, ruta) {
    const navegador = document.getElementById('navegadorArchivosRemoto');
    navegador.innerHTML = 'Cargando...';
    fetch('/listar_archivos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...datosConexion, ruta })
    })
    .then(res => res.json())
    .then(data => {
        if (!data.ok) {
            navegador.innerHTML = `<span style='color:red;'>${data.mensaje}</span>`;
            return;
        }
        let html = '';
        if (ruta !== '/' && ruta !== '' && ruta !== '.') {
            const rutaPadre = ruta.replace(/\/+$/, '').split('/').slice(0, -1).join('/') || '/';
            html += `<div style='margin-bottom:8px;'><a href='#' onclick='cargarArchivosRemotos(window._datosConexionRemoto, "${rutaPadre}");return false;'>⬆️ Subir</a></div>`;
        }
        html += '<ul style="list-style:none;padding-left:0;">';
        data.archivos.forEach(arch => {
            if (arch.es_directorio) {
                html += `<li><a href='#' onclick='cargarArchivosRemotos(window._datosConexionRemoto, "${ruta.replace(/\/+$/, '')}/${arch.nombre}");return false;'>📁 ${arch.nombre}</a></li>`;
            } else {
                html += `<li><a href='#' onclick='seleccionarArchivoRemoto("${ruta.replace(/\/+$/, '')}/${arch.nombre}");return false;'>📄 ${arch.nombre}</a></li>`;
            }
        });
        html += '</ul>';
        navegador.innerHTML = html;
    })
    .catch(err => {
        navegador.innerHTML = `<span style='color:red;'>Error: ${err}</span>`;
    });
}

function seleccionarArchivoRemoto(rutaCompleta) {
    // Rellenar el campo de ruta_log
    const form = document.querySelector('form[action="/add_server"]');
    form.querySelector('input[name="ruta_log"]').value = rutaCompleta;
    // Mostrar la sección de ruta si está oculta
    const seccion = document.getElementById('seccionRutaLog');
    if (seccion) seccion.style.display = '';
    // Cerrar el modal
    const modal = document.getElementById('modalSeleccionArchivo');
    if (modal) modal.remove();
}

// Modificar probarConexion para mostrar el modal si la conexión es exitosa
async function probarConexion() {
    const form = document.querySelector('form[action="/add_server"]');
    const ip = form.querySelector('input[name="ip_servidor"]').value;
    const usuario = form.querySelector('input[name="usuario_servidor"]').value;
    const password = form.querySelector('input[name="password_servidor"]').value;
    const puerto = form.querySelector('input[name="puerto"]').value || 22;
    const protocolo = form.querySelector('select[name="protocolo"]').value || 'SSH';
    const resultado = document.getElementById('resultadoConexion');

    resultado.innerHTML = '<span style="color: #888;">⏳ Probando conexión...</span>';

    try {
        const response = await fetch('/probar_conexion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ip, usuario, password, puerto, protocolo })
        });
        const data = await response.json();
        if (data.ok) {
            resultado.innerHTML = `<span style="color:green;">✔ ${data.mensaje}</span>`;
            // Guardar datos de conexión globalmente para navegación
            window._datosConexionRemoto = { ip, usuario, password, puerto, protocolo };
            mostrarModalSeleccionArchivo(window._datosConexionRemoto);
        } else {
            resultado.innerHTML = `<span style="color:red;">❌ ${data.mensaje}</span>`;
        }
    } catch (error) {
        resultado.innerHTML = `<span style="color:red;">❌ Error inesperado: ${error}</span>`;
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .highlight {
        background: rgba(255, 235, 59, 0.3) !important;
        transition: background 0.3s ease;
    }
    
    .dark-theme {
        filter: invert(1) hue-rotate(180deg);
    }
    
    .dark-theme img,
    .dark-theme video,
    .dark-theme svg {
        filter: invert(1) hue-rotate(180deg);
    }
`;
document.head.appendChild(style);