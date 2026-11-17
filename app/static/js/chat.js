function initChat() {
    // ============ Чат с ИИ (правая колонка) ============
    const chatMessages = document.getElementById('chatMessages');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const attachBtn = document.getElementById('attachBtn');
    const pdfInput = document.getElementById('pdfInput');
    const attachedList = document.getElementById('attachedList');
    const modeButtons = document.querySelectorAll('.toggle-btn-mode');

    let currentMode = 'normal';      // normal | document | sparql
    let attachedFiles = [];          // File[]

    // ID последнего полученного сообщения — для инкрементального опроса
    let lastMessageId = null;
    let pollTimer = null;

    const POLL_INTERVAL_MS = 3000;   // раз в 3 секунды

    // --- Отрисовка одного сообщения ---
    function renderMessage(msg) {
        const wrapper = document.createElement('div');
        wrapper.className = `msg msg-${msg.sender}`;   // role: 'user' | 'ai'
        wrapper.dataset.id = msg.id;

        const bubble = document.createElement('div');
        bubble.className = 'msg-bubble';
        bubble.textContent = msg.content;

        wrapper.appendChild(bubble);
        chatMessages.appendChild(wrapper);

        lastMessageId = msg.id;
    }

    // --- Прокрутка вниз ---
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // --- Добавить сообщение (локально) ---
    function addMessage(text, role) {
        renderMessage({ id: null, text, role });
        scrollToBottom();
    }

    // --- Загрузка всей истории ---
    async function loadHistory() {

        try {
            const response = await fetch(`/chat/msgs/${selected}`);
            if (!response.ok) throw new Error('HTTP ' + response.status);

            const messages = await response.json();   // [{ id, role, text }, ...]
            chatMessages.innerHTML = '';
            lastMessageId = null;

            messages.msgs.forEach(msg => renderMessage(msg));
            scrollToBottom();
        } catch (error) {
            console.error('Ошибка загрузки истории:', error);
            addMessage('Ошибка: не удалось загрузить историю сообщений', 'ai');
        }
    }

    // --- Опрос новых сообщений ---
    async function pollNewMessages() {
        try {
            const url = lastMessageId
                ? `/chat/new/${selected}/${lastMessageId}`
                : `/chat/msgs/${selected}`;

            const response = await fetch(url);
            if (!response.ok) throw new Error('HTTP ' + response.status);

            const data = await response.json();   // только новые
            const messages = data.msgs;

            if (!messages.length) return;

            // Был ли пользователь внизу до добавления?
            const wasAtBottom =
                chatMessages.scrollHeight - chatMessages.scrollTop - chatMessages.clientHeight < 40;

            //clearChat();
            messages.forEach(msg => renderMessage(msg));

            // Прокручиваем вниз, только если пользователь уже был внизу
            if (wasAtBottom) scrollToBottom();
        } catch (error) {
            console.error('Ошибка опроса сообщений:', error);
        }
    }

    function startPolling() {
        stopPolling();
        pollTimer = setInterval(pollNewMessages, POLL_INTERVAL_MS);
    }

    function stopPolling() {
        if (pollTimer !== null) {
            clearInterval(pollTimer);
            pollTimer = null;
        }
    }

    // Clear chat
    function clearChat() {
        chatMessages.innerHTML = '';
        lastMessageId = null;
    }

    // --- Отправка сообщения ---
    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        addMessage(text, 'user');
        chatInput.value = '';
        sendBtn.disabled = true;

        const formData = new FormData();
        formData.append('content', text);
        formData.append('mode', currentMode);
        formData.append('pid', selected);
        formData.append('sender', 'user');
        attachedFiles.forEach(file => formData.append('files', file));

        try {
            const response = await fetch('/chat/create', {
                method: 'POST',
                // body: formData,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode: currentMode, content: text, pid: selected, sender: 'user' }),
            });

            if (!response.ok) throw new Error('HTTP ' + response.status);

            clearChat();

            // const raw = await response.json();
            // const data = raw.msgs;

            // // Если сервер вернул сообщение с id — учтём, чтобы опрос его не дублировал
            // if (data.id != null) {
            //     renderMessage({ id: data.id, reply: data.content ?? 'Пустой ответ от сервера', role: 'ai' });
            //     scrollToBottom();
            // } else if (data.content) {
            //     addMessage(data.content, 'ai');
            // }

            // Сразу проверим новые сообщения (на случай, если ответ придёт асинхронно)
            pollNewMessages();
        } catch (error) {
            console.error('Ошибка отправки:', error);
            addMessage('Ошибка: не удалось получить ответ от сервера', 'ai');
        } finally {
            sendBtn.disabled = false;
            chatInput.focus();
        }
    }

    sendBtn.addEventListener('click', sendMessage);

    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // --- Toggle-кнопки режимов ---
    modeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            currentMode = btn.dataset.mode;
            modeButtons.forEach(b => b.classList.toggle('active', b === btn));
            console.log('Режим:', currentMode);
        });
    });

    // --- Прикрепление PDF ---
    attachBtn.addEventListener('click', () => pdfInput.click());

    pdfInput.addEventListener('change', () => {
        for (const file of pdfInput.files) {
            if (file.type !== 'application/pdf') continue;
            if (attachedFiles.some(f => f.name === file.name && f.size === file.size)) continue;
            attachedFiles.push(file);
        }
        pdfInput.value = '';
        renderAttached();
    });

    function renderAttached() {
        attachedList.innerHTML = '';
        attachedFiles.forEach((file, index) => {
            const li = document.createElement('li');

            const name = document.createElement('span');
            name.className = 'file-name';
            name.textContent = '📄 ' + file.name;
            name.title = file.name;

            const removeBtn = document.createElement('button');
            removeBtn.title = 'Убрать файл';
            removeBtn.textContent = '✕';
            removeBtn.addEventListener('click', () => {
                attachedFiles.splice(index, 1);
                renderAttached();
            });

            li.append(name, removeBtn);
            attachedList.appendChild(li);
        });
    }

    // --- Инициализация ---
    loadHistory().then(startPolling);

    // Останавливаем опрос при уходе со страницы
    window.addEventListener('beforeunload', stopPolling);
}