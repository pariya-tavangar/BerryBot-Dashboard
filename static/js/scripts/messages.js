    document.querySelectorAll('.use-template').forEach(btn => {
        btn.addEventListener('click', () => {
            const text = btn.querySelector('p').textContent;
            document.getElementById('message-body').value = text;
            document.getElementById('message-body').focus();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    });