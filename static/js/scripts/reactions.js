    document.querySelectorAll('.emoji-choice').forEach(b => b.addEventListener('click', () => {
        document.querySelectorAll('.emoji-choice').forEach(x => x.classList.remove('selected'));
        b.classList.add('selected');
        document.getElementById('chosen-emoji').value = b.dataset.emoji;
    }));