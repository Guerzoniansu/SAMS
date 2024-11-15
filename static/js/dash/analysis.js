
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






