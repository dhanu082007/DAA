document.addEventListener("DOMContentLoaded", function () {


    /* =====================================
       PRIORITY CALCULATION
    ===================================== */

    const severity = document.getElementById("severity");
    const priorityScore = document.getElementById("priorityScore");
    const priorityMessage = document.getElementById("priorityMessage");


    if (severity) {

        severity.addEventListener("change", function () {

            const selected = severity.value;

            const priorities = {

                "Critical": 100,
                "Severe": 80,
                "Moderate": 60,
                "Mild": 40,
                "Routine": 20

            };


            const messages = {

                "Critical":
                    "Highest priority. Requires immediate attention.",

                "Severe":
                    "High priority. Should be scheduled early.",

                "Moderate":
                    "Medium priority. Normal scheduling priority.",

                "Mild":
                    "Lower priority. Can be scheduled after urgent cases.",

                "Routine":
                    "Routine appointment priority."

            };


            if (selected && priorities[selected]) {

                priorityScore.textContent =
                    priorities[selected];

                priorityMessage.textContent =
                    messages[selected];

            }

            else {

                priorityScore.textContent = "--";

                priorityMessage.textContent =
                    "Select disease seriousness to calculate priority.";

            }

        });

    }


    /* =====================================
       PATIENT SEARCH
    ===================================== */

    const searchInput =
        document.getElementById("searchInput");

    const severityFilter =
        document.getElementById("severityFilter");

    const rows =
        document.querySelectorAll(".patient-row");


    function filterPatients() {

        const searchText =
            searchInput ?
            searchInput.value.toLowerCase() :
            "";

        const selectedSeverity =
            severityFilter ?
            severityFilter.value :
            "All";


        rows.forEach(function (row) {

            const rowText =
                row.textContent.toLowerCase();

            const rowSeverity =
                row.getAttribute("data-severity");


            const matchesSearch =
                rowText.includes(searchText);

            const matchesSeverity =
                selectedSeverity === "All" ||
                rowSeverity === selectedSeverity;


            if (matchesSearch && matchesSeverity) {

                row.style.display = "";

            }

            else {

                row.style.display = "none";

            }

        });

    }


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            filterPatients
        );

    }


    if (severityFilter) {

        severityFilter.addEventListener(
            "change",
            filterPatients
        );

    }


    /* =====================================
       PATIENT FORM VALIDATION
    ===================================== */

    const patientForm =
        document.getElementById("patientForm");


    if (patientForm) {

        patientForm.addEventListener(
            "submit",
            function (event) {

                const age =
                    document.getElementById("age").value;

                const phone =
                    document.getElementById("phone").value;


                if (age < 1 || age > 120) {

                    alert(
                        "Please enter a valid age."
                    );

                    event.preventDefault();

                    return;

                }


                if (!/^[0-9]{10}$/.test(phone)) {

                    alert(
                        "Please enter a valid 10-digit phone number."
                    );

                    event.preventDefault();

                    return;

                }

            }
        );

    }

});