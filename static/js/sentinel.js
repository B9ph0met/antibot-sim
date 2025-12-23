

// Run when page loads
window.addEventListener('DOMContentLoaded', function() {
    
    // Check for webdriver (most obvious sign)
    let isWebdriver = navigator.webdriver === true;
    
    // Check plugins (headless usually has 0)
    let pluginCount = navigator.plugins.length;
    
    // Check languages
    let hasLanguages = navigator.languages && navigator.languages.length > 0;
    
    // Calculate a simple headless score
    let headlessScore = 0;
    if (isWebdriver) headlessScore += 100;
    if (pluginCount === 0) headlessScore += 30;
    if (!hasLanguages) headlessScore += 20;
    
    headlessScore += checkEngine();
    
    document.getElementById('headless_score').value = headlessScore;

    document.getElementById('fingerprint').value = generateFingerprint();

});

function generateFingerprint() {
    let data = {
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        screenWidth: screen.width,
        screenHeight: screen.height,
        colorDepth: screen.colorDepth,
        timezoneOffset: new Date().getTimezoneOffset(),
        canvas: simpleHash(getCanvasFingerprint())
    };
    
    return btoa(JSON.stringify(data));
}

function checkEngine() {
    let score = 0;

    let alertStr = Function.prototype.toString.call(window.alert);
    if (alertStr.indexOf('[native code]') === -1) {
        score += 30;
    }

    if (window.__puppeteer_evaluation_script__ !== undefined) {
        score += 50;
    }

    if (!navigator.languages || navigator.languages.length === 0) {
        score += 20;
    }

    if (window.chrome && !window.chrome.runtime) {
        score += 10;
    }

    return score;
}

function getCanvasFingerprint() {
    let canvas = document.createElement('canvas');
    let ctx = canvas.getContext('2d');
    ctx.textBaseline = "top";
    ctx.font = "14px 'Arial'";
    ctx.textBaseline = "alphabetic";
    ctx.fillStyle = "#f60";
    ctx.fillRect(125,1,62,20);
    ctx.fillStyle = "#069";
    ctx.fillText("Cwm fjordbank glyphs vext quiz, 😃", 2, 15);
    ctx.fillStyle = "rgba(102, 204, 0, 0.7)";
    ctx.fillText("Cwm fjordbank glyphs vext quiz, 😃", 4, 17);
    return canvas.toDataURL();
}

function simpleHash(str) {
    let hash = 0, i, chr;
    if (str.length === 0) return hash;
    for (i = 0; i < str.length; i++) {
        chr   = str.charCodeAt(i);
        hash  = ((hash << 5) - hash) + chr;
        hash |= 0; // Convert to 32bit integer
    }
}

async function encryptWithPublicKey(publicKeyPem, data) {
    const pemContents = publicKeyPem
        .replace("-----BEGIN PUBLIC KEY-----", "")
        .replace("-----END PUBLIC KEY-----", "")
        .replace(/\s+/g, '');
        const binaryKey = Uint8Array.from(atob(pemContents), c => c.charCodeAt(0));

        const cryptoKey = await window.crypto.subtle.importKey(
        "spki",
        binaryKey.buffer,
        {
            name: "RSA-OAEP",
            hash: "SHA-256"
        },
        false,
        ["encrypt"]
    );

    const encodedData = new TextEncoder().encode(data);
    const encrypted = await crypto.subtle.encrypt(
        {
            name: "RSA-OAEP"},
        cryptoKey,
        encodedData
    );

    return btoa(String.fromCharCode(...new Uint8Array(encrypted)));
}

document.querySelector('form').addEventListener('submit', async function(e) {
    e.preventDefault();  // Stop normal submission
    
    const username = document.querySelector('input[name="username"]').value;
    const password = document.querySelector('input[name="password"]').value;
    
    // Encrypt both
    const encryptedUsername = await encryptWithPublicKey(PUBLIC_KEY, username);
    const encryptedPassword = await encryptWithPublicKey(PUBLIC_KEY, password);
    
    // Set hidden fields
    document.getElementById('encrypted_username').value = encryptedUsername;
    document.getElementById('encrypted_password').value = encryptedPassword;

    document.querySelector('input[name="username"]').value = '';
    document.querySelector('input[name="password"]').value = '';
    
    // Now submit
    this.submit();
});