document.addEventListener("click", function (e) {
    const btn = e.target.closest('.see-more-btn');

    if (btn) {
        e.preventDefault();

        const container = btn.closest(".custom_job_description_container");

        if (!container) return;

        const shortText = container.querySelector(".short-text");
        const fullText = container.querySelector(".full-text");
        const icon = btn.querySelector('i');

        if (!shortText || !fullText) return;

        if (fullText.classList.contains("d-none")) {
            // Show full text
            shortText.classList.add("d-none");
            fullText.classList.remove("d-none");

            // Change button text and icon for "See less"
            btn.innerHTML = '<i class="fa fa-chevron-circle-up me-1"></i> See less';
        } else {
            // Show short text
            shortText.classList.remove("d-none");
            fullText.classList.add("d-none");

            // Change button text and icon for "See more"
            btn.innerHTML = '<i class="fa fa-chevron-circle-down me-1"></i> See more';
        }
    }
});

console.log("JS Loaded");