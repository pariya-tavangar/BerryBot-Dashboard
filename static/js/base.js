    (function () {
      const c = document.getElementById('desktop-crumb');
      if (c && window.innerWidth > 720) c.style.display = 'block';
      window.addEventListener('resize', () => {
        if (c) c.style.display = window.innerWidth > 720 ? 'block' : 'none'
      });
    })();

    function useTemplate(text) {
      const field = document.getElementById('message-body');
      if (field) {
        field.value = text;
        field.focus();
      }
    }