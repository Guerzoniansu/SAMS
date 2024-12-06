// document.addEventListener("DOMContentLoaded", () => {
//     const dateList = document.querySelector(".foot .head-cont .dates .scrollable-dates");
//     const calendarIcon = document.querySelector(".foot .head-cont .calendar");
//     const datePicker = document.querySelector(".foot .head-cont #datePicker");

//     // Populate the list of dates
//     const today = new Date();
//     const startDate = new Date(today.getFullYear(), 0, 1); // January 1st of the current year
//     let currentDate = startDate;

//     while (currentDate <= today) {
//         const dateString = currentDate.toISOString().split("T")[0]; // Format: YYYY-MM-DD
//         const listItem = document.createElement("li");
//         listItem.textContent = dateString;
//         listItem.dataset.date = dateString;
//         dateList.appendChild(listItem);

//         currentDate.setDate(currentDate.getDate() + 1); // Increment by 1 day
//     }

//     // Show the date picker on calendar SVG click
//     calendarIcon.addEventListener("click", () => {
//         datePicker.click();
//     });

//     // Navigate to the selected date
//     datePicker.addEventListener("change", (event) => {
//         const selectedDate = event.target.value;
//         const targetElement = [...dateList.children].find(
//             (li) => li.dataset.date === selectedDate
//         );
//         if (targetElement) {
//             targetElement.scrollIntoView({ behavior: "smooth", block: "center" });
//         }
//     });
// });

const today = new Date();
const currentYear = today.getFullYear();
const nextYear = currentYear + 1;

const minDate = `2010-01-01`;
const year = today.getFullYear();
const month = String(today.getMonth() + 1).padStart(2, '0'); // Add 1 to month as it's zero-based
const day = String(today.getDate()).padStart(2, '0');

// Combine into YYYY-MM-DD
const today_f = `${year}-${month}-${day}`;
const maxDate = today_f;

const dateInput = document.querySelector(".foot .head-cont #datePicker");
dateInput.min = minDate;
dateInput.max = maxDate;
dateInput.value = maxDate


const pld = document.querySelector("#selectPd");
pld.min = minDate;
pld.max = maxDate;
pld.value = maxDate



function setSelected() {
    const urlParams = new URLSearchParams(window.location.search);
    const imgd = urlParams.get('imgd') || today_f;
    const param = urlParams.get('param') || "arvi";
    const pd = urlParams.get('pd') || today_f;
    const crop = urlParams.get('crop') || "whea";

    // Debugging: Check if values are being correctly set
    console.log({ imgd, param, pd, crop });

    document.getElementById("datePicker").value = imgd;
    document.getElementById("selectParam").value = param;
    document.getElementById("selectPd").value = pd;
    document.getElementById("selectCul").value = crop;
}

function update() {
    const date = document.getElementById("datePicker").value;
    const param = document.getElementById("selectParam").value;
    const selectedPd = document.getElementById("selectPd").value;
    const selectedCrop = document.getElementById("selectCul").value;

    // Debugging: Check captured values
    console.log({ date, param, selectedPd, selectedCrop });

    const url = new URL(window.location.href);
    url.searchParams.set('imgd', date);
    url.searchParams.set('param', param);
    url.searchParams.set('pd', selectedPd);
    url.searchParams.set('crop', selectedCrop);
    window.location.href = url.toString(); // Reload with new parameters
}

window.onload = setSelected;



