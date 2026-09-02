/** @odoo-module **/

function setLoaderVisible(visible) {
    for (const loader of document.querySelectorAll(".ab-page-loader")) {
        loader.classList.toggle("is-hidden", !visible);
    }
}

function hideLoader() {
    window.setTimeout(() => setLoaderVisible(false), 120);
}

if (document.readyState === "complete") {
    hideLoader();
} else {
    window.addEventListener("load", hideLoader, { once: true });
}

document.addEventListener("submit", (event) => {
    if (event.target.closest("body[class*='ab-template-']")) {
        setLoaderVisible(true);
    }
});

window.setTimeout(() => setLoaderVisible(false), 5000);
