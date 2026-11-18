// Selected proc
var selected = -1;

document.addEventListener('DOMContentLoaded', async () => {
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

            // При открытии вкладки файлов — запрос на сервер
            if (targetId === 'tab-files') {
                loadFiles();
            }
            if (targetId === 'tab-yaml') {
                loadYaml();
            }
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

    initList();

    // ============ Вкладка "Файлы" ============
    const fileList = document.getElementById('fileList');

    // Форматирование размера
    function formatSize(bytes) {
        if (bytes == null || isNaN(bytes)) return '';
        if (bytes < 1024) return bytes + ' Б';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' КБ';
        if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' МБ';
        return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' ГБ';
    }

    // Загрузка списка файлов
    async function loadFiles() {
        fileList.innerHTML = '<li class="file-loading">Загрузка...</li>';

        try {
            const response = await fetch(`/chat/pdf/${selected}`, {
                method: 'GET',
                headers: { 'Accept': 'application/json' },
            });

            if (!response.ok) throw new Error('HTTP ' + response.status);

            const files = (await response.json()).files;   // [{ id, name, size }, ...]

            renderFiles(files);
        } catch (error) {
            console.error('Ошибка загрузки файлов:', error);
            fileList.innerHTML = '<li class="file-error">Не удалось загрузить список файлов</li>';
        }
    }

    function renderFiles(files) {
        fileList.innerHTML = '';

        if (!Array.isArray(files) || files.length === 0) {
            const empty = document.createElement('li');
            empty.className = 'file-empty';
            empty.textContent = 'Файлов пока нет';
            fileList.appendChild(empty);
            return;
        }

        files.forEach(file => {
            const li = document.createElement('li');
            li.className = 'file-item';
            li.dataset.id = file.id;

            const icon = document.createElement('div');
            icon.className = 'file-icon';
            icon.textContent = '📄';

            const info = document.createElement('div');
            info.className = 'file-info';

            const name = document.createElement('span');
            name.className = 'file-name';
            name.textContent = file.name;
            name.title = file.name;

            const size = document.createElement('span');
            size.className = 'file-size';
            size.textContent = formatSize(file.size);

            info.append(name, size);

            const delBtn = document.createElement('button');
            delBtn.className = 'file-delete';
            delBtn.title = 'Удалить файл';
            delBtn.textContent = '✕';
            delBtn.addEventListener('click', () => deleteFile(file, delBtn));

            li.append(icon, info, delBtn);
            fileList.appendChild(li);
        });
    }

    async function deleteFile(file, btn) {
        if (!confirm(`Удалить файл «${file.name}»?`)) return;

        btn.disabled = true;

        try {
            const response = await fetch(`/chat/pdf/${selected}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: file.id, name: file.name }),
            });

            if (!response.ok) throw new Error('HTTP ' + response.status);

            // Удаляем элемент из DOM
            const li = btn.closest('.file-item');
            if (li) li.remove();

            // Если список опустел — показать "Файлов пока нет"
            if (!fileList.querySelector('.file-item')) {
                const empty = document.createElement('li');
                empty.className = 'file-empty';
                empty.textContent = 'Файлов пока нет';
                fileList.appendChild(empty);
            }
        } catch (error) {
            console.error('Ошибка удаления:', error);
            btn.disabled = false;
            alert('Не удалось удалить файл');
        }
    }

    // Экспортируем наружу, если нужно вызывать из других мест
    window.loadFiles = loadFiles;

    // ============ Вкладка "YAML" ============
    const yamlEditor = document.getElementById('yamlEditor');
    const loadYamlBtn = document.getElementById('loadYamlBtn');
    const sendYamlBtn = document.getElementById('sendYamlBtn');
    const yamlFileInput = document.getElementById('yamlFileInput');
    const yamlStatus = document.getElementById('yamlStatus');

    async function loadYaml() {
        const response = await fetch(`/ontology/yaml/${selected}`, {
            method: 'GET'
        });

        if (!response.ok) throw new Error('HTTP ' + response.status);

        const data = (await response.json()).text;
        yamlEditor.value = data;
    }

    function setYamlStatus(text, type) {
        yamlStatus.textContent = text || '';
        yamlStatus.className = 'yaml-status' + (type ? ' ' + type : '');
    }

    // --- Загрузка YAML-файла в редактор ---
    loadYamlBtn.addEventListener('click', (e) => {
        e.preventDefault();
        yamlFileInput.click();     // синхронно, в рамках user activation
    });

    yamlFileInput.addEventListener('change', async () => {
        const file = yamlFileInput.files[0];
        yamlFileInput.value = '';  // сброс, чтобы можно было выбрать тот же файл снова
        if (!file) return;

        try {
            const text = await file.text();   // читаем содержимое как текст
            yamlEditor.value = text;
            setYamlStatus(`Загружен файл: ${file.name} (${file.size} Б)`, 'ok');
        } catch (error) {
            console.error('Ошибка чтения файла:', error);
            setYamlStatus('Не удалось прочитать файл', 'err');
        }
    });

    // --- Отправка текста на сервер ---
    sendYamlBtn.addEventListener('click', async () => {
        const text = yamlEditor.value.trim();
        if (!text) {
            setYamlStatus('Поле пустое — нечего отправлять', 'err');
            return;
        }

        sendYamlBtn.disabled = true;
        setYamlStatus('Отправка...');

        try {
            const response = await fetch(`/ontology/yaml/${selected}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text }),
            });

            if (!response.ok) throw new Error('HTTP ' + response.status);

            const data = await response.json().catch(() => ({}));
            setYamlStatus(
                'Отправлено успешно',
                'ok'
            );
        } catch (error) {
            console.error('Ошибка отправки YAML:', error);
            setYamlStatus('Не удалось отправить на сервер', 'err');
        } finally {
            sendYamlBtn.disabled = false;
        }
    });
});