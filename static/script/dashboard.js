document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById('search-input');
    const otpGrid = document.getElementById('otp-grid');
    const spoilers = document.querySelectorAll(".spoiler");
    const copyButtons = document.querySelectorAll('.copy-btn');
    const copyNotification = document.getElementById('copy-notification');

    function highlightText(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    let debounceTimer;
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            const searchValue = this.value.toLowerCase();
            const cards = document.querySelectorAll('.card');
            let hasResults = false;
            
            cards.forEach(card => {
                const nameElement = card.querySelector('h3');
                const name = nameElement.textContent.toLowerCase();
                if (name.includes(searchValue)) {
                    card.style.display = '';
                    nameElement.innerHTML = highlightText(nameElement.textContent, searchValue);
                    hasResults = true;
                } else {
                    card.style.display = 'none';
                    nameElement.innerHTML = nameElement.textContent; // Remove previous highlights
                }
            });

            if (!hasResults) {
                document.querySelector('.no-secrets-message').style.display = 'block';
            } else {
                document.querySelector('.no-secrets-message').style.display = 'none';
            }
        }, 300); // Adjust debounce delay as needed
    });

    spoilers.forEach(spoiler => {
        const secret = spoiler.getAttribute("data-secret");
        spoiler.addEventListener("mouseenter", () => {
            spoiler.textContent = secret;
        });
        spoiler.addEventListener("mouseleave", () => {
            spoiler.textContent = "Zum Anzeigen hover";
        });
    });

    function animateDigits(element, newCode) {
        const digits = newCode.split('');
        element.innerHTML = '';

        digits.forEach((digit, index) => {
            const span = document.createElement('span');
            span.textContent = digit;
            span.style.animationDelay = `${index * 0.1}s`;
            element.appendChild(span);
        });
    }

    function fetchAndUpdateCodes() {
        fetch('/get_secrets_by_company/' + kundennummer)
            .then(response => response.json())
            .then(data => {
                data.forEach(secret => {
                    const otpCodeElement = document.getElementById(`otp-code-${secret.name}`);
                    if (otpCodeElement) {
                        animateDigits(otpCodeElement, secret.otp_code);
                    }
                });
            })
            .catch(error => console.error('Error fetching OTP codes:', error));
    }

    function startOtpUpdateInterval() {
        fetchAndUpdateCodes();
        updateCountdownTimer();

        const now = new Date();
        const secondsUntilNext30 = 30 - (now.getSeconds() % 30);
        setTimeout(() => {
            fetchAndUpdateCodes();
            setInterval(fetchAndUpdateCodes, 30000);
        }, secondsUntilNext30 * 1000);
        
        setInterval(updateCountdownTimer, 1000);
    }

    function updateCountdownTimer() {
        const now = new Date();
        const seconds = now.getSeconds();
        const countdown = 30 - (seconds % 30);

        const refreshTimeElements = document.querySelectorAll(".refresh-time");
        refreshTimeElements.forEach(element => {
            element.textContent = `${countdown}s`;
        });
    }

    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const otpId = this.getAttribute('data-otp');
            const otpElement = document.getElementById(otpId);
            if (otpElement) {
                const otpCode = otpElement.textContent;
                navigator.clipboard.writeText(otpCode).then(() => {
                    console.log('OTP copied to clipboard:', otpCode);
                    copyNotification.classList.add('show');
                    setTimeout(() => {
                        copyNotification.classList.remove('show');
                    }, 4000); 
                }).catch(err => {
                    console.error('Error copying OTP:', err);
                });
            }
        });
    });

    startOtpUpdateInterval();
});