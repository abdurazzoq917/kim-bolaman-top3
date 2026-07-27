document.addEventListener(
    "DOMContentLoaded",
    () => {
        const form = document.querySelector(
            "#careerForm"
        );

        if (!form) {
            return;
        }

        const questionCards =
            form.querySelectorAll(
                ".question-card"
            );

        const answeredCountElement =
            document.querySelector(
                "#answeredCount"
            );

        const progressBar =
            document.querySelector(
                "#progressBar"
            );

        function updateProgress() {
            let completedQuestions = 0;

            questionCards.forEach(
                (questionCard) => {
                    const selectedInputs =
                        questionCard.querySelectorAll(
                            'input[type="checkbox"]:checked'
                        );

                    const counter =
                        questionCard.querySelector(
                            ".selected-counter strong"
                        );

                    counter.textContent =
                        selectedInputs.length;

                    if (
                        selectedInputs.length >= 1
                    ) {
                        completedQuestions += 1;
                    }
                }
            );

            answeredCountElement.textContent =
                completedQuestions;

            const progressPercent =
                (
                    completedQuestions
                    / questionCards.length
                )
                * 100;

            progressBar.style.width =
                `${progressPercent}%`;
        }

        questionCards.forEach(
            (questionCard) => {
                const checkboxes =
                    questionCard.querySelectorAll(
                        'input[type="checkbox"]'
                    );

                checkboxes.forEach(
                    (checkbox) => {
                        checkbox.addEventListener(
                            "change",
                            () => {
                                const selectedInputs =
                                    questionCard
                                        .querySelectorAll(
                                            'input[type="checkbox"]:checked'
                                        );

                                if (
                                    selectedInputs.length > 2
                                ) {
                                    checkbox.checked =
                                        false;

                                    alert(
                                        "Bu savolda ko‘pi bilan 2 ta javob tanlash mumkin."
                                    );
                                }

                                updateProgress();
                            }
                        );
                    }
                );
            }
        );

        form.addEventListener(
            "submit",
            (event) => {
                for (
                    let index = 0;
                    index < questionCards.length;
                    index += 1
                ) {
                    const questionCard =
                        questionCards[index];

                    const selectedInputs =
                        questionCard.querySelectorAll(
                            'input[type="checkbox"]:checked'
                        );

                    if (
                        selectedInputs.length < 1
                    ) {
                        event.preventDefault();

                        questionCard.scrollIntoView(
                            {
                                behavior: "smooth",
                                block: "center",
                            }
                        );

                        alert(
                            `${index + 1}-savolda kamida 1 ta javob tanlang.`
                        );

                        return;
                    }

                    if (
                        selectedInputs.length > 2
                    ) {
                        event.preventDefault();

                        alert(
                            `${index + 1}-savolda ko‘pi bilan 2 ta javob tanlang.`
                        );

                        return;
                    }
                }
            }
        );

        updateProgress();
    }
);