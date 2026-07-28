document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("careerForm");

    // main.js boshqa sahifalarda ham ulangan bo‘lishi mumkin.
    // Forma topilmasa, kod xatosiz to‘xtaydi.
    if (!form) {
        return;
    }

    const questionCards = form.querySelectorAll(".question-card");
    const answeredCountElement =
        document.getElementById("answeredCount");
    const progressBar =
        document.getElementById("progressBar");
    const submitButton =
        form.querySelector('button[type="submit"]');

    let isSubmitting = false;

    function updateProgress() {
        let completedQuestions = 0;

        questionCards.forEach((questionCard) => {
            const selectedInputs =
                questionCard.querySelectorAll(
                    'input[type="checkbox"]:checked'
                );

            const counter =
                questionCard.querySelector(
                    ".selected-counter strong"
                );

            if (counter) {
                counter.textContent =
                    String(selectedInputs.length);
            }

            if (selectedInputs.length >= 1) {
                completedQuestions += 1;
            }
        });

        if (answeredCountElement) {
            answeredCountElement.textContent =
                String(completedQuestions);
        }

        if (progressBar && questionCards.length > 0) {
            const progressPercent =
                (completedQuestions / questionCards.length) * 100;

            progressBar.style.width =
                `${progressPercent}%`;

            progressBar.setAttribute(
                "aria-valuenow",
                String(Math.round(progressPercent))
            );
        }
    }

    function showQuestionError(questionCard, message) {
        questionCard.scrollIntoView({
            behavior: "smooth",
            block: "center",
        });

        questionCard.classList.add("question-error");

        window.setTimeout(() => {
            questionCard.classList.remove("question-error");
        }, 2000);

        alert(message);
    }

    questionCards.forEach((questionCard) => {
        const checkboxes =
            questionCard.querySelectorAll(
                'input[type="checkbox"]'
            );

        checkboxes.forEach((checkbox) => {
            checkbox.addEventListener("change", () => {
                const selectedInputs =
                    questionCard.querySelectorAll(
                        'input[type="checkbox"]:checked'
                    );

                if (selectedInputs.length > 2) {
                    checkbox.checked = false;

                    alert(
                        "Bu savolda ko‘pi bilan 2 ta javob tanlash mumkin."
                    );
                }

                updateProgress();
            });
        });
    });

    form.addEventListener("submit", (event) => {
        if (isSubmitting) {
            event.preventDefault();
            return;
        }

        for (
            let index = 0;
            index < questionCards.length;
            index += 1
        ) {
            const questionCard = questionCards[index];

            const selectedInputs =
                questionCard.querySelectorAll(
                    'input[type="checkbox"]:checked'
                );

            if (selectedInputs.length < 1) {
                event.preventDefault();

                showQuestionError(
                    questionCard,
                    `${index + 1}-savolda kamida 1 ta javob tanlang.`
                );

                return;
            }

            if (selectedInputs.length > 2) {
                event.preventDefault();

                showQuestionError(
                    questionCard,
                    `${index + 1}-savolda ko‘pi bilan 2 ta javob tanlang.`
                );

                return;
            }
        }

        isSubmitting = true;
        form.classList.add("loading");

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.dataset.originalText =
                submitButton.textContent.trim();

            submitButton.textContent =
                "Natija hisoblanmoqda...";
        }
    });

    // Brauzer orqaga qaytganda tugma bloklangan
    // holatda qolib ketmasligi uchun.
    window.addEventListener("pageshow", () => {
        isSubmitting = false;
        form.classList.remove("loading");

        if (submitButton) {
            submitButton.disabled = false;

            if (submitButton.dataset.originalText) {
                submitButton.textContent =
                    submitButton.dataset.originalText;
            }
        }

        updateProgress();
    });

    updateProgress();
});