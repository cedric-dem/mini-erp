function applyTheme(theme) {
    if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    } else {
        document.documentElement.removeAttribute('data-theme');
    }
    document.cookie = `mini-erp-theme=${theme}; path=/; max-age=31536000; SameSite=Lax`;
}

function getCookie(name) {
    const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
    return match ? decodeURIComponent(match[1]) : null;
}

function openInventoryModal() {
    const modal = document.getElementById('inventoryModal');
    if (modal) modal.style.display = 'flex';
}

function closeInventoryModal() {
    const modal = document.getElementById('inventoryModal');
    if (modal) modal.style.display = 'none';
}

function openInventoryMovementModal(itemId, movementType, itemName) {
    const modal = document.getElementById('inventoryMovementModal');
    const itemIdInput = document.getElementById('movementItemId');
    const movementTypeInput = document.getElementById('movementType');
    const title = document.getElementById('movementModalTitle');

    if (!modal || !itemIdInput || !movementTypeInput || !title) return;

    itemIdInput.value = String(itemId);
    movementTypeInput.value = movementType;
    title.textContent = `${movementType === 'add' ? 'Add' : 'Delete'} movement for ${itemName}`;
    modal.style.display = 'flex';
}

function closeInventoryMovementModal() {
    const modal = document.getElementById('inventoryMovementModal');
    if (modal) modal.style.display = 'none';
}

document.addEventListener('click', (event) => {
    const inventoryModal = document.getElementById('inventoryModal');
    const movementModal = document.getElementById('inventoryMovementModal');

    if (inventoryModal && event.target === inventoryModal) {
        closeInventoryModal();
    }

    if (movementModal && event.target === movementModal) {
        closeInventoryMovementModal();
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const savedTheme = getCookie('mini-erp-theme') === 'dark' ? 'dark' : 'light';
    applyTheme(savedTheme);

    if (darkModeToggle) {
        darkModeToggle.checked = savedTheme === 'dark';
        darkModeToggle.addEventListener('change', () => {
            applyTheme(darkModeToggle.checked ? 'dark' : 'light');
        });
    }
});