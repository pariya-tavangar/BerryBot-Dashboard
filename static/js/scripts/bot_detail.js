let botActive = true; 

(function () {
    const copyText = async (value, button) => {
        if (!value) return;

        try {
            await navigator.clipboard.writeText(value);
            if (button) {
                const previous = button.textContent;
                button.textContent = "Copied!";
                window.setTimeout(() => button.textContent = previous, 1300);
            }
        } catch (error) {
            if (button) button.textContent = "Copy failed";
        }
    };

    document.querySelectorAll("[data-copy]").forEach((button) => {
        button.addEventListener("click", () => {
            copyText(button.dataset.copy, button);
        });
    });

    const tokenInput = document.getElementById("botToken");
    const toggleToken = document.getElementById("toggleToken");
    const copyToken = document.getElementById("copyToken");

    if (tokenInput && toggleToken) {
        toggleToken.addEventListener("click", () => {
            const isHidden = tokenInput.type === "password";
            tokenInput.type = isHidden ? "text" : "password";
            toggleToken.textContent = isHidden ? "Hide" : "Show";
        });
    }

    if (tokenInput && copyToken) {
        copyToken.addEventListener("click", () => {
            copyText(tokenInput.value, copyToken);
        });
    }

    const copyBotId = document.getElementById("copyBotId");
    if (copyBotId) {
        copyBotId.addEventListener("click", () => {
            copyText(copyBotId.dataset.copy, copyBotId);
        });
    }
})();