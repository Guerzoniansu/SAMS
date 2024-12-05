
function getDynamicColor(v) {
    v = parseInt(v)
    if (v >50) {
        return "rgb(0, 184, 147)";
    }
    else if (v<50) {
        return "rgb(230, 25, 66)";
    }
    else {
        return "rgb(253, 205, 13)";
    }
}

progress_fills = document.querySelectorAll(".card.first .subcard.point .cont .subcont.third table tbody tr td .progress-bar .progress-fill")

/* document.addEventListener("DOMContentLoaded", function() {
    progress_fills.forEach(p => {
        v = p.getAttribute("data-percent")
        p.style.background = getDynamicColor(v)
    });
}) */

const currentYear = new Date().getFullYear();
const nextYear = currentYear + 1;

const minDate = `${nextYear}-01-01`;
const maxDate = `${nextYear}-12-31`;

const dateInput = document.getElementById("selectPd");
dateInput.min = minDate;
dateInput.max = maxDate;
dateInput.value = minDate

function setSelected() {
    const urlParams = new URLSearchParams(window.location.search);
    const pd = urlParams.get('pd') || '2025-01-01';
    const crops = urlParams.get('crop') || 'whea';
    const type = urlParams.get('tgp') || 'max';
    document.getElementById("selectPd").value = pd;
    document.getElementById("selectCrop").value = crops
    document.getElementById("selectType").value = type
}

function update() {
    const selectedPd = document.getElementById("selectPd").value;
    const selectedCrop = document.getElementById("selectCrop").value;
    const selectedType = document.getElementById("selectType").value;

    const url = new URL(window.location.href);
    url.searchParams.set('pd', selectedPd);
    url.searchParams.set('crop', selectedCrop);
    url.searchParams.set('type', selectedType);
    window.location.href = url.toString();
}

window.onload = setSelected;






