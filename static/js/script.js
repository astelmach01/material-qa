document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Generate a random user ID for the session
    let userId = localStorage.getItem('userId');
    if (!userId) {
        userId = 'user_' + Math.random().toString(36).substring(2, 15);
        localStorage.setItem('userId', userId);
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const query = userInput.value.trim();
        if (query === '') {
            return;
        }

        appendMessage({ answer: query }, 'user');
        userInput.value = '';

        fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query, user_id: userId }),
        })
            .then(response => response.json())
            .then(data => {
                appendMessage(data, 'bot');
            })
            .catch(error => {
                console.error('Error:', error);
                appendMessage({ answer: 'Sorry, something went wrong.' }, 'bot');
            });
    }

    function appendMessage(data, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);

        const answerElement = document.createElement('p');
        answerElement.textContent = data.answer;
        messageElement.appendChild(answerElement);

        if (data.articles && data.articles.length > 0) {
            const articlesElement = document.createElement('div');
            articlesElement.classList.add('articles');
            data.articles.forEach(article => {
                const articleElement = document.createElement('div');
                articleElement.classList.add('article');
                articleElement.innerHTML = article.replace(/\n/g, '<br>');
                articlesElement.appendChild(articleElement);
            });
            messageElement.appendChild(articlesElement);
        }

        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});
