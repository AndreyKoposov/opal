document.addEventListener('DOMContentLoaded', () => {
    // --- Переключение вкладок в центральной колонке ---
    const menuButtons = document.querySelectorAll('.menu-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    menuButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.dataset.tab;

            menuButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            tabPanels.forEach(panel => {
                panel.classList.toggle('active', panel.id === targetId);
            });
        });
    });

    // --- Сворачивание / разворачивание боковых колонок ---
    const layout = document.getElementById('layout');
    const leftColumn = document.getElementById('leftColumn');
    const rightColumn = document.getElementById('rightColumn');
    const toggleLeft = document.getElementById('toggleLeft');
    const toggleRight = document.getElementById('toggleRight');

    toggleLeft.addEventListener('click', () => {
        leftColumn.classList.toggle('collapsed');
        const collapsed = leftColumn.classList.contains('collapsed');
        toggleLeft.textContent = collapsed ? '▶' : '◀';
        toggleLeft.title = collapsed ? 'Показать левую колонку' : 'Скрыть левую колонку';
    });

    toggleRight.addEventListener('click', () => {
        rightColumn.classList.toggle('collapsed');
        const collapsed = rightColumn.classList.contains('collapsed');
        toggleRight.textContent = collapsed ? '◀' : '▶';
        toggleRight.title = collapsed ? 'Показать правую колонку' : 'Скрыть правую колонку';
    });
});