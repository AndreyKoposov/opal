async function initList() {
    // --- Список элементов в левой колонке ---
    const itemList = document.getElementById('itemList');
    const addItemBtn = document.getElementById('addItem');

    // Начальные данные (потом можно грузить с сервера)
    // let items = [
    //     { id: 1, name: 'Иван Петров' },
    //     { id: 2, name: 'Мария Смирнова' },
    //     { id: 3, name: 'Алексей Кузнецов' },
    // ];

    function getCookie(name) {
        const match = document.cookie.match(
            new RegExp('(?:^|; )' + name.replace(/([.*+?^${}()|[\]\\])/g, '\\$1') + '=([^;]*)')
        );
        return match ? decodeURIComponent(match[1]) : null;
    }

    // Cookies
    const user_id = getCookie('user_id');

    // Load items
    const response = await fetch(`/processes/list/${user_id.value}`, {method: 'GET'});
    let p_json = await response.json();
    let items = p_json.processes;

    // Инициалы для аватарки
    function getInitials(name) {
        return name
            .trim()
            .split(/\s+/)
            .slice(0, 2)
            .map(w => w[0])
            .join('')
            .toUpperCase();
    }

    // Отрисовка всего списка
    function renderItems() {
        itemList.innerHTML = '';

        if (items.length === 0) {
            const empty = document.createElement('li');
            empty.className = 'item-name';
            empty.style.padding = '0.5rem';
            empty.style.color = '#999';
            empty.textContent = 'Список пуст';
            itemList.appendChild(empty);
            return;
        }

        items.forEach(item => {
            const li = document.createElement('li');
            li.className = 'item';
            li.dataset.id = item.id;
            li.setAttribute('role', 'button');
            li.setAttribute('tabindex', '0');

            // Аватарка
            const avatar = document.createElement('div');
            avatar.className = 'item-avatar';
            avatar.textContent = getInitials(item.name);

            // Название
            const name = document.createElement('span');
            name.className = 'item-name';
            name.textContent = item.name;
            name.title = item.name;

            // Кнопки
            const actions = document.createElement('div');
            actions.className = 'item-actions';

            const editBtn = document.createElement('button');
            editBtn.className = 'item-action edit';
            editBtn.title = 'Редактировать';
            editBtn.textContent = '✎';
            editBtn.addEventListener('click', (e) => {
                e.stopPropagation();   // не всплываем до клика по элементу
                editItem(item.id);
            });

            const delBtn = document.createElement('button');
            delBtn.className = 'item-action delete';
            delBtn.title = 'Удалить';
            delBtn.textContent = '✕';
            delBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                deleteItem(item.id);
            });

            actions.append(editBtn, delBtn);

            // Клик по самому элементу
            li.addEventListener('click', () => selectItem(item.id));
            // Поддержка клавиатуры
            li.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    selectItem(item.id);
                }
            });

            li.append(avatar, name, actions);
            itemList.appendChild(li);
        });
    }

    // Добавление
    addItemBtn.addEventListener('click', async () => {
        const name = prompt('Название нового элемента:');
        if (!name || !name.trim()) return;

        const newItem = {
            id: -1,
            name: name.trim(),
        };
        items.push(newItem);
        renderItems();

        // Cookies
        //const user_id = await cookieStore.get('user_id');
        const user_id = getCookie('user_id');

        // Пример отправки на сервер:
        const response = await fetch('/processes/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: -1, name: newItem.name, user: parseInt(user_id.value) }),
        });
        let json = await response.json();
        newItem.id = json.pid;
    });

    // Редактирование
    function editItem(id) {
        const item = items.find(i => i.id === id);
        if (!item) return;

        const newName = prompt('Новое название:', item.name);
        if (newName === null) return;          // отмена
        if (!newName.trim()) return;           // пустое — игнорируем

        item.name = newName.trim();
        renderItems();

        fetch(`/processes/update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: id, name: item.name, user: 0 }),
        });
    }

    // Удаление
    function deleteItem(id) {
        if (!confirm('Удалить элемент?')) return;

        items = items.filter(i => i.id !== id);
        renderItems();

        fetch(`/processes/delete/`, { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: id, name: " ", user: 0 }),
        });
    }

        // Клик по элементу
    function selectItem(id) {
        const item = items.find(i => i.id === id);
        if (!item) return;

        console.log('Выбран элемент:', item);
        selected = id;
        initChat();

        // Отправка на сервер информации о нажатии
        // fetch('/api/items/select', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify({
        //         id: item.id,
        //         name: item.name,
        //         clicked_at: new Date().toISOString(),
        //     }),
        // })
        // .then(response => response.json())
        // .then(data => console.log('Ответ сервера:', data))
        // .catch(error => console.error('Ошибка отправки:', error));
    }

    renderItems();
}