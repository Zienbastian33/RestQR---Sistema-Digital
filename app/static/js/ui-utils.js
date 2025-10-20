/**
 * UI Utilities - Sistema de notificaciones y helpers de UI
 */

// Sistema de Toasts Modernos
const Toast = {
    /**
     * Muestra un toast con el mensaje y tipo especificado
     * @param {string} message - Mensaje a mostrar
     * @param {string} type - Tipo de toast: 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duración en ms (default: 3000)
     */
    show: function(message, type = 'info', duration = 3000) {
        const toastContainer = this.getOrCreateContainer();

        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast align-items-center text-white bg-${this.getBootstrapColor(type)} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="${this.getIcon(type)} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        toastContainer.appendChild(toast);

        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: duration
        });

        bsToast.show();

        // Remover del DOM después de ocultarse
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    success: function(message, duration = 3000) {
        this.show(message, 'success', duration);
    },

    error: function(message, duration = 4000) {
        this.show(message, 'error', duration);
    },

    warning: function(message, duration = 3500) {
        this.show(message, 'warning', duration);
    },

    info: function(message, duration = 3000) {
        this.show(message, 'info', duration);
    },

    getOrCreateContainer: function() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        return container;
    },

    getBootstrapColor: function(type) {
        const colors = {
            'success': 'success',
            'error': 'danger',
            'warning': 'warning',
            'info': 'info'
        };
        return colors[type] || 'info';
    },

    getIcon: function(type) {
        const icons = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };
        return icons[type] || 'fas fa-info-circle';
    }
};

// Loading States Manager
const LoadingState = {
    /**
     * Activa el estado de carga en un botón
     * @param {HTMLElement} button - Botón a modificar
     * @param {string} loadingText - Texto durante carga (default: 'Cargando...')
     * @returns {Object} Estado original del botón
     */
    start: function(button, loadingText = 'Cargando...') {
        const originalState = {
            text: button.innerHTML,
            disabled: button.disabled
        };

        button.disabled = true;
        button.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            ${loadingText}
        `;

        return originalState;
    },

    /**
     * Restaura el estado original del botón
     * @param {HTMLElement} button - Botón a restaurar
     * @param {Object} originalState - Estado original del botón
     */
    stop: function(button, originalState) {
        button.disabled = originalState.disabled;
        button.innerHTML = originalState.text;
    }
};

// Modal de Confirmación
const ConfirmModal = {
    /**
     * Muestra un modal de confirmación
     * @param {Object} options - Opciones del modal
     * @param {string} options.title - Título del modal
     * @param {string} options.message - Mensaje de confirmación
     * @param {string} options.confirmText - Texto del botón confirmar (default: 'Confirmar')
     * @param {string} options.cancelText - Texto del botón cancelar (default: 'Cancelar')
     * @param {string} options.type - Tipo: 'danger', 'warning', 'info' (default: 'info')
     * @param {Function} options.onConfirm - Callback al confirmar
     * @param {Function} options.onCancel - Callback al cancelar (opcional)
     * @returns {Promise} Promise que se resuelve con true/false
     */
    show: function(options) {
        return new Promise((resolve) => {
            const {
                title = '¿Está seguro?',
                message = '¿Desea continuar con esta acción?',
                confirmText = 'Confirmar',
                cancelText = 'Cancelar',
                type = 'info',
                onConfirm = null,
                onCancel = null
            } = options;

            // Crear modal si no existe
            let modal = document.getElementById('confirm-modal');
            if (!modal) {
                modal = document.createElement('div');
                modal.id = 'confirm-modal';
                modal.className = 'modal fade';
                modal.setAttribute('tabindex', '-1');
                modal.innerHTML = `
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="confirm-modal-title"></h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body" id="confirm-modal-message"></div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" id="confirm-modal-cancel"></button>
                                <button type="button" class="btn" id="confirm-modal-confirm"></button>
                            </div>
                        </div>
                    </div>
                `;
                document.body.appendChild(modal);
            }

            // Configurar contenido
            document.getElementById('confirm-modal-title').textContent = title;
            document.getElementById('confirm-modal-message').textContent = message;
            document.getElementById('confirm-modal-cancel').textContent = cancelText;

            const confirmBtn = document.getElementById('confirm-modal-confirm');
            confirmBtn.textContent = confirmText;
            confirmBtn.className = `btn btn-${type === 'danger' ? 'danger' : type === 'warning' ? 'warning' : 'primary'}`;

            const bsModal = new bootstrap.Modal(modal);

            // Event handlers
            const handleConfirm = () => {
                bsModal.hide();
                if (onConfirm) onConfirm();
                resolve(true);
                cleanup();
            };

            const handleCancel = () => {
                bsModal.hide();
                if (onCancel) onCancel();
                resolve(false);
                cleanup();
            };

            const cleanup = () => {
                confirmBtn.removeEventListener('click', handleConfirm);
                modal.removeEventListener('hidden.bs.modal', handleCancel);
            };

            confirmBtn.addEventListener('click', handleConfirm);
            modal.addEventListener('hidden.bs.modal', handleCancel, { once: true });

            bsModal.show();
        });
    }
};

// Utility para copiar al portapapeles con feedback
const Clipboard = {
    /**
     * Copia texto al portapapeles con feedback visual
     * @param {string} text - Texto a copiar
     * @param {HTMLElement} button - Botón que disparó la acción (opcional)
     */
    copy: async function(text, button = null) {
        try {
            await navigator.clipboard.writeText(text);
            Toast.success('Copiado al portapapeles');

            if (button) {
                const originalIcon = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => {
                    button.innerHTML = originalIcon;
                }, 1000);
            }
        } catch (err) {
            // Fallback para navegadores antiguos
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            document.body.appendChild(textArea);
            textArea.select();

            try {
                document.execCommand('copy');
                Toast.success('Copiado al portapapeles');
            } catch (err) {
                Toast.error('No se pudo copiar al portapapeles');
            }

            document.body.removeChild(textArea);
        }
    }
};

// Estado Vacío (Empty State)
const EmptyState = {
    /**
     * Crea un elemento de estado vacío
     * @param {Object} options - Opciones del estado vacío
     * @param {string} options.icon - Clase de icono Font Awesome
     * @param {string} options.message - Mensaje a mostrar
     * @param {string} options.submessage - Submensaje (opcional)
     * @returns {HTMLElement} Elemento del estado vacío
     */
    create: function(options) {
        const {
            icon = 'fas fa-inbox',
            message = 'No hay elementos',
            submessage = ''
        } = options;

        const emptyState = document.createElement('div');
        emptyState.className = 'empty-state text-center py-5';
        emptyState.innerHTML = `
            <i class="${icon} fa-3x text-muted mb-3"></i>
            <p class="text-muted mb-1">${message}</p>
            ${submessage ? `<small class="text-muted">${submessage}</small>` : ''}
        `;

        return emptyState;
    }
};

// Formateo de precios
const PriceFormatter = {
    /**
     * Formatea un precio al formato local
     * @param {number} price - Precio a formatear
     * @param {string} currency - Código de moneda (default: 'CLP')
     * @returns {string} Precio formateado
     */
    format: function(price, currency = 'CLP') {
        return new Intl.NumberFormat('es-CL', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(price);
    }
};

// Exportar para uso global
window.Toast = Toast;
window.LoadingState = LoadingState;
window.ConfirmModal = ConfirmModal;
window.Clipboard = Clipboard;
window.EmptyState = EmptyState;
window.PriceFormatter = PriceFormatter;
