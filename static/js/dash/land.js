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



function setSelected() {
    const urlParams = new URLSearchParams(window.location.search);
    const imgd = urlParams.get('imgd') || today_f;
    document.getElementById("datePicker").value = imgd;
}

function update() {
    const sel = document.getElementById("datePicker").value;
    const url = new URL(window.location.href);
    url.searchParams.set('imgd', sel);
    window.location.href = url.toString();
}

window.onload = setSelected;




