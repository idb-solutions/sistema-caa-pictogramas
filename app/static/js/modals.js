/**
 * Sistema de Modais Personalizados
 * Substitui alert() e confirm() por modais bonitos
 */

// Criar estrutura HTML dos modais
document.addEventListener('DOMContentLoaded', () => {
    if (!document.getElementById('customModalContainer')) {
        const modalHTML = `
            <!-- Modal de Alerta -->
            <div id="customAlertModal" class="modal-overlay" style="display: none; z-index: 9999;">
                <div class="modal" onclick="event.stopPropagation()" style="max-width: 450px;">
                    <div style="text-align: center; margin-bottom: 20px;">
                        <div id="alertIcon" style="width: 60px; height: 60px; margin: 0 auto 16px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem;">
                        </div>
                        <h2 id="alertTitle" style="margin-bottom: 8px;"></h2>
                        <p id="alertMessage" style="color: var(--gray-600); line-height: 1.6;"></p>
                    </div>
                    <div class="modal-actions">
                        <button onclick="closeCustomAlert()" class="btn-primary btn-block">
                            OK
                        </button>
                    </div>
                </div>
            </div>

            <!-- Modal de Confirmação -->
            <div id="customConfirmModal" class="modal-overlay" style="display: none; z-index: 9999;">
                <div class="modal" onclick="event.stopPropagation()" style="max-width: 450px;">
                    <div style="text-align: center; margin-bottom: 20px;">
                        <div style="width: 60px; height: 60px; margin: 0 auto 16px; background: linear-gradient(135deg, var(--warning), #F59E0B); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem;">
                            ⚠️
                        </div>
                        <h2 id="confirmTitle" style="margin-bottom: 8px;">Confirmar ação</h2>
                        <p id="confirmMessage" style="color: var(--gray-600); line-height: 1.6;"></p>
                    </div>
                    <div class="modal-actions">
                        <button onclick="confirmCustomAction(true)" class="btn-primary">
                            Confirmar
                        </button>
                        <button onclick="confirmCustomAction(false)" class="btn-secondary">
                            Cancelar
                        </button>
                    </div>
                </div>
            </div>
        `;

        const container = document.createElement('div');
        container.id = 'customModalContainer';
        container.innerHTML = modalHTML;
        document.body.appendChild(container);
    }
});

// Variável para armazenar callback do confirm
let confirmCallback = null;

/**
 * Exibe modal de alerta personalizado
 * @param {string} message - Mensagem a ser exibida
 * @param {string} type - Tipo: 'success', 'error', 'warning', 'info'
 */
function showAlert(message, type = 'info') {
    const modal = document.getElementById('customAlertModal');
    const icon = document.getElementById('alertIcon');
    const title = document.getElementById('alertTitle');
    const messageEl = document.getElementById('alertMessage');

    // Configurar ícone e cores baseado no tipo
    const configs = {
        success: {
            icon: '✓',
            bg: 'linear-gradient(135deg, var(--success), #10B981)',
            title: 'Sucesso!'
        },
        error: {
            icon: '✕',
            bg: 'linear-gradient(135deg, var(--danger), #EF4444)',
            title: 'Erro!'
        },
        warning: {
            icon: '⚠️',
            bg: 'linear-gradient(135deg, var(--warning), #F59E0B)',
            title: 'Atenção!'
        },
        info: {
            icon: 'ℹ️',
            bg: 'linear-gradient(135deg, var(--info), #3B82F6)',
            title: 'Informação'
        }
    };

    const config = configs[type] || configs.info;

    icon.textContent = config.icon;
    icon.style.background = config.bg;
    icon.style.color = 'white';
    title.textContent = config.title;
    messageEl.textContent = message;

    modal.style.display = 'flex';

    // Fechar com ESC
    const escHandler = (e) => {
        if (e.key === 'Escape') {
            closeCustomAlert();
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
}

/**
 * Fecha o modal de alerta
 */
function closeCustomAlert() {
    const modal = document.getElementById('customAlertModal');
    modal.style.display = 'none';
}

/**
 * Exibe modal de confirmação personalizado
 * @param {string} message - Mensagem de confirmação
 * @returns {Promise<boolean>} - true se confirmado, false se cancelado
 */
function showConfirm(message) {
    return new Promise((resolve) => {
        const modal = document.getElementById('customConfirmModal');
        const messageEl = document.getElementById('confirmMessage');

        messageEl.textContent = message;
        modal.style.display = 'flex';

        confirmCallback = (result) => {
            modal.style.display = 'none';
            resolve(result);
        };

        // Fechar com ESC = cancelar
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                confirmCustomAction(false);
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    });
}

/**
 * Processa resposta do modal de confirmação
 */
function confirmCustomAction(result) {
    if (confirmCallback) {
        confirmCallback(result);
        confirmCallback = null;
    }
}

// Exportar para uso global
window.showAlert = showAlert;
window.showConfirm = showConfirm;
window.closeCustomAlert = closeCustomAlert;
window.confirmCustomAction = confirmCustomAction;
