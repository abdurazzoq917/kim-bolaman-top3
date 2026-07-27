document.addEventListener(
    "DOMContentLoaded",
    function () {
        const form =
            document.getElementById(
                "careerForm"
            );

        if (!form) {
            console.error(
                'Xato: id="careerForm" bo‘lgan forma topilmadi.'
            );

            return;
        }

        const questionCards =
            form.querySelectorAll(
                ".question-card"
            );

        const answeredCountElement =
            document.getElementById(
                "answeredCount"
            );

        const progressBar =
            document.getElementById(
                "progressBar"
            );

        function updateProgress() {
            let completedQuestions = 0;

            questionCards.forEach(
                function (questionCard) {
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
                            selectedInputs.length;
                    }

                    if (
                        selectedInputs.length >= 1
                    ) {
                        completedQuestions += 1;
                    }
                }
            );

            if (answeredCountElement) {
                answeredCountElement.textContent =
                    completedQuestions;
            }

            if (
                progressBar &&
                questionCards.length > 0
            ) {
                const progressPercent =
                    (
                        completedQuestions /
                        questionCards.length
                    ) * 100;

                progressBar.style.width =
                    progressPercent + "%";
            }
        }

        questionCards.forEach(
            function (questionCard) {
                const checkboxes =
                    questionCard.querySelectorAll(
                        'input[type="checkbox"]'
                    );

                checkboxes.forEach(
                    function (checkbox) {
                        checkbox.addEventListener(
                            "change",
                            function () {
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
            function (event) {
                for (
                    let index = 0;
                    index < questionCards.length;
                    index += 1
                ) {
                    const questionCard =
                        questionCards[index];

                    const selectedInputs =
                        questionCard
                            .querySelectorAll(
                                'input[type="checkbox"]:checked'
                            );

                    if (
                        selectedInputs.length < 1
                    ) {
                        event.preventDefault();

                        questionCard.scrollIntoView({
                            behavior: "smooth",
                            block: "center"
                        });

                        alert(
                            `${index + 1}-savolda kamida 1 ta javob tanlang.`
                        );

                        return;
                    }

                    if (
                        selectedInputs.length > 2
                    ) {
                        event.preventDefault();

                        questionCard.scrollIntoView({
                            behavior: "smooth",
                            block: "center"
                        });

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